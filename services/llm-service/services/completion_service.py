from typing import Optional, List, Dict, Any
from openai import OpenAI

from common import get_settings


settings = get_settings()


class CompletionService:
    """文本补全服务"""
    
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
            print(f"✗ Completion 服务初始化失败: {str(e)}")
    
    def create_completion(
        self,
        model: str = "gpt-3.5-turbo-instruct",
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
                raise Exception("Completion service not initialized")
            
            response = self._client.completions.create(
                model=model,
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
        """获取支持的补全模型"""
        return [
            {
                "id": "gpt-3.5-turbo-instruct",
                "name": "GPT-3.5 Turbo Instruct",
                "max_tokens": 4096,
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
        ]


completion_service = CompletionService()
