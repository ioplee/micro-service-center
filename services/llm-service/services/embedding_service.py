from typing import Optional, List, Dict, Any
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer

from common import get_settings


settings = get_settings()


class EmbeddingService:
    """Embedding 服务"""
    
    def __init__(self):
        self._openai_client = None
        self._local_model = None
        self._init_clients()
    
    def _init_clients(self):
        """初始化客户端"""
        try:
            if settings.openai_api_key:
                client_kwargs = {"api_key": settings.openai_api_key}
                if settings.openai_base_url:
                    client_kwargs["base_url"] = settings.openai_base_url
                
                self._openai_client = OpenAI(**client_kwargs)
                print("✓ OpenAI 客户端初始化成功")
            
            try:
                self._local_model = SentenceTransformer("all-MiniLM-L6-v2")
                print("✓ 本地 Embedding 模型加载成功")
            except Exception as e:
                print(f"⚠ 本地 Embedding 模型加载失败: {str(e)}")
        except Exception as e:
            print(f"✗ Embedding 服务初始化失败: {str(e)}")
    
    def create_embedding(
        self,
        input_texts: List[str],
        model: str = "text-embedding-3-small",
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建文本嵌入"""
        try:
            if self._openai_client and model.startswith("text-embedding"):
                # 使用 OpenAI
                response = self._openai_client.embeddings.create(
                    input=input_texts,
                    model=model,
                    encoding_format=encoding_format,
                    dimensions=dimensions,
                    user=user,
                )
                
                return {
                    "object": "list",
                    "data": [
                        {
                            "object": "embedding",
                            "index": idx,
                            "embedding": item.embedding,
                        }
                        for idx, item in enumerate(response.data)
                    ],
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                }
            elif self._local_model:
                # 使用本地模型
                embeddings = self._local_model.encode(input_texts)
                
                return {
                    "object": "list",
                    "data": [
                        {
                            "object": "embedding",
                            "index": idx,
                            "embedding": embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                        }
                        for idx, embedding in enumerate(embeddings)
                    ],
                    "model": "local-sentence-transformer",
                    "usage": {
                        "prompt_tokens": sum(len(text.split()) for text in input_texts),
                        "total_tokens": sum(len(text.split()) for text in input_texts),
                    },
                }
            else:
                raise Exception("No embedding client available")
        except Exception as e:
            raise Exception(f"创建文本嵌入错误: {str(e)}")
    
    def calculate_similarity(
        self,
        vectors1: List[List[float]],
        vectors2: List[List[float]],
        metric: str = "cosine",
    ) -> List[List[float]]:
        """计算向量相似度"""
        try:
            if len(vectors1) != len(vectors2):
                raise Exception("向量数量不匹配")
            
            results = []
            
            for v1, v2 in zip(vectors1, vectors2):
                v1_np = np.array(v1)
                v2_np = np.array(v2)
                
                if metric == "cosine":
                    similarity = np.dot(v1_np, v2_np) / (np.linalg.norm(v1_np) * np.linalg.norm(v2_np))
                elif metric == "euclidean":
                    distance = np.linalg.norm(v1_np - v2_np)
                    similarity = 1 / (1 + distance)
                elif metric == "dot":
                    similarity = np.dot(v1_np, v2_np)
                else:
                    raise Exception(f"不支持的相似度度量: {metric}")
                
                results.append(float(similarity))
            
            return results
        except Exception as e:
            raise Exception(f"计算相似度错误: {str(e)}")
    
    def semantic_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
        model: str = "text-embedding-3-small",
    ) -> List[Dict[str, Any]]:
        """向量搜索"""
        try:
            # 创建查询嵌入
            query_result = self.create_embedding(
                input_texts=[query],
                model=model,
            )
            query_embedding = query_result["data"][0]["embedding"]
            
            # 创建文档嵌入
            docs_result = self.create_embedding(
                input_texts=documents,
                model=model,
            )
            doc_embeddings = [item["embedding"] for item in docs_result["data"]]
            
            # 计算相似度
            similarities = self.calculate_similarity(
                vectors1=[query_embedding] * len(doc_embeddings),
                vectors2=doc_embeddings,
                metric="cosine",
            )
            
            # 排序并返回 top_k
            results = [
                {
                    "document_id": idx,
                    "document": documents[idx],
                    "similarity": similarities[idx],
                    "rank": idx,
                }
                for idx in range(len(documents))
            ]
            
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return results[:top_k]
        except Exception as e:
            raise Exception(f"向量搜索错误: {str(e)}")
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """获取支持的嵌入模型"""
        models = [
            {
                "id": "text-embedding-3-small",
                "name": "Text Embedding 3 Small",
                "dimension": 1536,
                "type": "openai",
            },
            {
                "id": "text-embedding-3-large",
                "name": "Text Embedding 3 Large",
                "dimension": 3072,
                "type": "openai",
            },
            {
                "id": "text-embedding-ada-002",
                "name": "Text Embedding Ada 002",
                "dimension": 1536,
                "type": "openai",
            },
        ]
        
        if self._local_model:
            models.append({
                "id": "local-sentence-transformer",
                "name": "Local Sentence Transformer",
                "dimension": self._local_model.get_sentence_embedding_dimension(),
                "type": "local",
            })
        
        return models


embedding_service = EmbeddingService()
