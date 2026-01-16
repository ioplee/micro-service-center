from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time
import httpx

from common import ServiceResponse


router = APIRouter()


LLM_SERVICE = "http://localhost:8003"


class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False


class ChatWithHistoryRequest(BaseModel):
    user_id: str
    message: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_history: int = 20


# 简单的聊天历史存储（生产环境应使用数据库）
chat_histories: Dict[str, List[Dict[str, str]]] = {}


@router.post("/completions", tags=["Chat"], summary="聊天补全")
async def chat_completions(request: ChatRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE}/chat/completions",
                json={
                    "model": request.model,
                    "messages": [m.dict() for m in request.messages],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": request.stream,
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data=response_data,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Chat completion failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.post("/with-history", tags=["Chat"], summary="带历史的聊天")
async def chat_with_history(request: ChatWithHistoryRequest):
    try:
        # 获取用户历史
        if request.user_id not in chat_histories:
            chat_histories[request.user_id] = []
        
        history = chat_histories[request.user_id]
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": "你是一个友好的智能助手。"}
        ]
        
        # 添加历史记录
        messages.extend(history[-request.max_history:])
        
        # 添加当前消息
        messages.append({"role": "user", "content": request.message})
        
        # 调用 LLM
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE}/chat/completions",
                json={
                    "model": request.model,
                    "messages": messages,
                    "temperature": request.temperature,
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        # 提取回答
        answer = response_data["data"]["choices"][0]["message"]["content"]
        
        # 更新历史记录
        history.append({"role": "user", "content": request.message})
        history.append({"role": "assistant", "content": answer})
        
        # 限制历史长度
        if len(history) > request.max_history * 2:
            chat_histories[request.user_id] = history[-request.max_history * 2:]
        
        return ServiceResponse(
            success=True,
            data={
                "user_id": request.user_id,
                "message": request.message,
                "response": answer,
                "history_length": len(chat_histories[request.user_id]),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Chat with history failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.get("/history/{user_id}", tags=["Chat"], summary="获取聊天历史")
async def get_chat_history(user_id: str, limit: int = Query(20, ge=1, le=100)):
    try:
        if user_id not in chat_histories:
            return ServiceResponse(
                success=True,
                data={"user_id": user_id, "history": [], "total_count": 0},
                version="1.0.0",
                timestamp=time.time(),
            )
        
        history = chat_histories[user_id]
        
        return ServiceResponse(
            success=True,
            data={
                "user_id": user_id,
                "history": history[-limit:],
                "total_count": len(history),
                "returned_count": min(limit, len(history)),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Get chat history failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.delete("/history/{user_id}", tags=["Chat"], summary="清除聊天历史")
async def clear_chat_history(user_id: str):
    try:
        if user_id in chat_histories:
            del chat_histories[user_id]
        
        return ServiceResponse(
            success=True,
            data={"user_id": user_id, "message": "聊天历史已清除"},
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Clear chat history failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.post("/summarize", tags=["Chat"], summary="总结对话")
async def summarize_conversation(
    user_id: str = Body(...),
    max_length: int = Body(200, ge=50, le=1000),
):
    try:
        if user_id not in chat_histories:
            return ServiceResponse(
                success=False,
                error=f"No chat history found for user {user_id}",
                version="1.0.0",
                timestamp=time.time(),
            )
        
        history = chat_histories[user_id]
        
        # 构建对话文本
        conversation = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in history
        ])
        
        # 调用 LLM 总结
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLM_SERVICE}/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"请用不超过 {max_length} 字总结以下对话内容。",
                        },
                        {
                            "role": "user",
                            "content": conversation,
                        },
                    ],
                    "max_tokens": max_length,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        summary = response_data["data"]["choices"][0]["message"]["content"]
        
        return ServiceResponse(
            success=True,
            data={
                "user_id": user_id,
                "summary": summary,
                "original_messages": len(history),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Summarize conversation failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )
