from typing import Optional, List, Dict, Any
from openai import OpenAI

from common import get_settings


settings = get_settings()


class ChatService:
    """聊天服务"""
    
    def __init__(self):
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        try:
            if settings.openai_api_key:
                client_kwargs = {"api_key": settings.openai_api_key}
                if settings.openai_base_url:
                    client_kwargs["base_url"] = settings.openai_base_url
                
                self._client = OpenAI(**client_kwargs)
                print("✓ OpenAI 客户端初始化成功")
        except Exception as e:
            print(f"✗ Chat 服务初始化失败: {str(e)}")
    
    def create_chat_completion(
        self,
        model: str = "gpt-3.5-turbo",
        messages: List[Dict[str, Any]] = None,
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        stream: bool = False,
        stop: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建聊天补全"""
        try:
            if not self._client:
                raise Exception("Chat service not initialized")
            
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                n=n,
                stream=stream,
                stop=stop,
                max_tokens=max_tokens,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                user=user,
            )
            
            if stream:
                # 流式响应处理
                return {
                    "id": response.id,
                    "object": "chat.completion.chunk",
                    "created": response.created,
                    "model": response.model,
                    "choices": [
                        {
                            "index": choice.index,
                            "delta": {
                                "role": choice.delta.role,
                                "content": choice.delta.content,
                            },
                            "finish_reason": choice.finish_reason,
                        }
                        for choice in response.choices
                    ],
                }
            else:
                return {
                    "id": response.id,
                    "object": "chat.completion",
                    "created": response.created,
                    "model": response.model,
                    "choices": [
                        {
                            "index": choice.index,
                            "message": {
                                "role": choice.message.role,
                                "content": choice.message.content,
                            },
                            "finish_reason": choice.finish_reason,
                        }
                        for choice in response.choices
                    ],
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                }
        except Exception as e:
            raise Exception(f"创建聊天补全错误: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取支持的聊天模型"""
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "max_tokens": 16384,
                "type": "openai",
            },
            {
                "id": "gpt-3.5-turbo-16k",
                "name": "GPT-3.5 Turbo 16k",
                "max_tokens": 16384,
                "type": "openai",
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "max_tokens": 8192,
                "type": "openai",
            },
            {
                "id": "gpt-4-turbo-preview",
                "name": "GPT-4 Turbo Preview",
                "max_tokens": 128000,
                "type": "openai",
            },
            {
                "id": "gpt-4-vision-preview",
                "name": "GPT-4 Vision Preview",
                "max_tokens": 128000,
                "type": "openai",
            },
        ]


chat_service = ChatService()
