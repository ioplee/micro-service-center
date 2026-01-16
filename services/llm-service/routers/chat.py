from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, LLMException
from services import vllm_service


router = APIRouter()


class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo"
    messages: List[Message]
    temperature: float = 0.7
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    stop: Optional[List[str]] = None
    max_tokens: Optional[int] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    user: Optional[str] = None


@router.post("/completions", tags=["Chat"], summary="创建聊天补全")
async def create_chat_completion(request: ChatCompletionRequest):
    try:
        result = vllm_service.create_chat_completion(
            model=request.model,
            messages=[m.dict() for m in request.messages],
            temperature=request.temperature,
            top_p=request.top_p,
            n=request.n,
            stream=request.stream,
            stop=request.stop,
            max_tokens=request.max_tokens,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
            user=request.user,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Create chat completion failed: {str(e)}",
            error_code="CHAT_COMPLETION_CREATE_FAILED",
        )


@router.post("/completions/stream", tags=["Chat"], summary="流式聊天补全")
async def create_chat_completion_stream(
    model: str = Body("gpt-3.5-turbo"),
    messages: List[Message] = Body(...),
    temperature: float = Body(0.7),
    top_p: float = Body(1.0),
    stop: Optional[List[str]] = Body(None),
    max_tokens: Optional[int] = Body(None),
    user: Optional[str] = Body(None),
):
    try:
        result = vllm_service.create_chat_completion(
            model=model,
            messages=[m.dict() for m in messages],
            temperature=temperature,
            top_p=top_p,
            stream=True,
            stop=stop,
            max_tokens=max_tokens,
            user=user,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Create chat completion stream failed: {str(e)}",
            error_code="CHAT_COMPLETION_STREAM_FAILED",
        )


@router.post("/completions/batch", tags=["Chat"], summary="批量聊天补全")
async def batch_chat_completion(
    conversations: List[List[Message]] = Body(...),
    model: str = Body("gpt-3.5-turbo"),
    temperature: float = Body(0.7),
    top_p: float = Body(1.0),
    max_tokens: Optional[int] = Body(None),
):
    try:
        results = []
        
        for idx, conversation in enumerate(conversations):
            result = vllm_service.create_chat_completion(
                model=model,
                messages=[m.dict() for m in conversation],
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
            )
            
            results.append({
                "id": idx,
                "result": result,
            })
        
        return ServiceResponse(
            success=True,
            data={
                "total_count": len(results),
                "results": results,
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Batch chat completion failed: {str(e)}",
            error_code="BATCH_CHAT_COMPLETION_FAILED",
        )


@router.get("/models", tags=["Chat"], summary="获取支持的模型")
async def get_chat_models():
    try:
        models = vllm_service.get_available_models()
        return ServiceResponse(
            success=True,
            data={
                "models": models,
                "total_count": len(models),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Get chat models failed: {str(e)}",
            error_code="GET_CHAT_MODELS_FAILED",
        )
