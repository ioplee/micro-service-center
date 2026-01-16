from typing import Optional, List, Dict, Any
from openai import OpenAI

from common import get_settings


settings = get_settings()


class VLLMService:
    """vLLM 服务 - 高性能 LLM 推理"""
    
    def __init__(self):
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        try:
            client_kwargs = {
                "base_url": settings.vllm_base_url,
            }
            
            if settings.vllm_api_key:
                client_kwargs["api_key"] = settings.vllm_api_key
            else:
                client_kwargs["api_key"] = "token-abc123"  # vLLM 默认不需要 API Key
            
            self._client = OpenAI(**client_kwargs)
            print("✓ vLLM 客户端初始化成功")
        except Exception as e:
            print(f"✗ vLLM 服务初始化失败: {str(e)}")
    
    def create_chat_completion(
        self,
        model: str = None,
        messages: List[Dict[str, Any]] = None,
        temperature: float = 0.7,
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
                raise Exception("vLLM service not initialized")
            
            response = self._client.chat.completions.create(
                model=model or settings.vllm_model,
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
    
    def create_completion(
        self,
        model: str = None,
        prompt: str = "",
        suffix: Optional[str] = None,
        max_tokens: int = 16,
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        stream: bool = False,
        logprobs: Optional[int] = None,
        echo: bool = False,
        stop: Optional[List[str]] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        best_of: int = 1,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建文本补全"""
        try:
            if not self._client:
                raise Exception("vLLM service not initialized")
            
            response = self._client.completions.create(
                model=model or settings.vllm_model,
                prompt=prompt,
                suffix=suffix,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                n=n,
                stream=stream,
                logprobs=logprobs,
                echo=echo,
                stop=stop,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                best_of=best_of,
                user=user,
            )
            
            return {
                "id": response.id,
                "object": "text_completion",
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "text": choice.text,
                        "index": choice.index,
                        "logprobs": choice.logprobs,
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
            raise Exception(f"创建文本补全错误: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        try:
            if not self._client:
                return []
            
            models = self._client.models.list()
            return [
                {
                    "id": model.id,
                    "name": model.id,
                    "type": "vllm",
                }
                for model in models.data
            ]
        except Exception as e:
            print(f"获取模型列表失败: {str(e)}")
            return [
                {
                    "id": settings.vllm_model,
                    "name": settings.vllm_model,
                    "type": "vllm",
                }
            ]


vllm_service = VLLMService()
