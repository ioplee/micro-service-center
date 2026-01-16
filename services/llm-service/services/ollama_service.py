from typing import Optional, List, Dict, Any
import httpx

from common import get_settings


settings = get_settings()


class OllamaEmbeddingService:
    """Ollama Embedding 服务 - 用于生成文本嵌入"""
    
    def __init__(self):
        self._base_url = f"http://{settings.ollama_host}:{settings.ollama_port}"
        self._model = settings.ollama_embedding_model
        self._init_client()
    
    def _init_client(self):
        """初始化客户端"""
        try:
            print(f"✓ Ollama 服务初始化成功 (host: {settings.ollama_host}:{settings.ollama_port}, model: {self._model})")
        except Exception as e:
            print(f"✗ Ollama 服务初始化失败: {str(e)}")
    
    def create_embedding(
        self,
        input: List[str] = None,
        model: str = None,
    ) -> Dict[str, Any]:
        """创建嵌入向量"""
        try:
            if not input:
                raise ValueError("input 参数不能为空")
            
            if isinstance(input, str):
                input = [input]
            
            model = model or self._model
            
            results = []
            
            for text in input:
                with httpx.Client(timeout=30.0) as client:
                    response = client.post(
                        f"{self._base_url}/api/embeddings",
                        json={
                            "model": model,
                            "prompt": text,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    results.append({
                        "object": "embedding",
                        "embedding": data["embedding"],
                        "index": len(results),
                    })
            
            return {
                "object": "list",
                "data": results,
                "model": model,
                "usage": {
                    "prompt_tokens": sum(len(text.split()) for text in input),
                    "total_tokens": sum(len(text.split()) for text in input),
                },
            }
        except httpx.HTTPError as e:
            raise Exception(f"Ollama 请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"创建嵌入向量错误: {str(e)}")
    
    def batch_create_embedding(
        self,
        input: List[str] = None,
        model: str = None,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """批量创建嵌入向量"""
        try:
            if not input:
                raise ValueError("input 参数不能为空")
            
            if isinstance(input, str):
                input = [input]
            
            model = model or self._model
            
            results = []
            
            for i in range(0, len(input), batch_size):
                batch = input[i:i + batch_size]
                
                with httpx.Client(timeout=60.0) as client:
                    for text in batch:
                        response = client.post(
                            f"{self._base_url}/api/embeddings",
                            json={
                                "model": model,
                                "prompt": text,
                            },
                        )
                        response.raise_for_status()
                        data = response.json()
                        
                        results.append({
                            "object": "embedding",
                            "embedding": data["embedding"],
                            "index": len(results),
                        })
            
            return {
                "object": "list",
                "data": results,
                "model": model,
                "usage": {
                    "prompt_tokens": sum(len(text.split()) for text in input),
                    "total_tokens": sum(len(text.split()) for text in input),
                },
            }
        except Exception as e:
            raise Exception(f"批量创建嵌入向量错误: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取支持的模型"""
        try:
            with httpx.Client() as client:
                response = client.get(f"{self._base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                
                return [
                    {
                        "id": model["name"],
                        "name": model["name"],
                        "size": model.get("size", ""),
                        "digest": model.get("digest", ""),
                        "type": "ollama",
                    }
                    for model in data.get("models", [])
                ]
        except Exception as e:
            print(f"获取 Ollama 模型列表失败: {str(e)}")
            return [
                {
                    "id": self._model,
                    "name": self._model,
                    "type": "ollama",
                }
            ]


ollama_embedding_service = OllamaEmbeddingService()
