from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, LLMException
from services import ollama_embedding_service


router = APIRouter()


class EmbeddingRequest(BaseModel):
    input: List[str]
    model: str = None


class BatchEmbeddingRequest(BaseModel):
    input: List[str]
    model: str = None
    batch_size: int = 10


@router.post("/create", tags=["Embedding"], summary="创建嵌入向量")
async def create_embedding(request: EmbeddingRequest):
    try:
        result = ollama_embedding_service.create_embedding(
            input=request.input,
            model=request.model,
        )
        
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Create embedding failed: {str(e)}",
            error_code="EMBEDDING_CREATE_FAILED",
        )


@router.post("/create/batch", tags=["Embedding"], summary="批量创建嵌入向量")
async def batch_create_embedding(request: BatchEmbeddingRequest):
    try:
        result = ollama_embedding_service.batch_create_embedding(
            input=request.input,
            model=request.model,
            batch_size=request.batch_size,
        )
        
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Batch create embedding failed: {str(e)}",
            error_code="EMBEDDING_BATCH_CREATE_FAILED",
        )


@router.get("/models", tags=["Embedding"], summary="获取支持的嵌入模型")
async def get_embedding_models():
    try:
        models = ollama_embedding_service.get_available_models()
        
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
            detail=f"Get embedding models failed: {str(e)}",
            error_code="EMBEDDING_GET_MODELS_FAILED",
        )


@router.post("/similarity", tags=["Embedding"], summary="计算相似度")
async def calculate_similarity(
    texts: List[str] = Body(..., min_length=2),
    model: str = None,
):
    try:
        if len(texts) < 2:
            raise ValueError("至少需要两个文本进行相似度计算")
        
        # 创建嵌入向量
        result = ollama_embedding_service.create_embedding(
            input=texts,
            model=model,
        )
        
        embeddings = [item["embedding"] for item in result["data"]]
        
        # 计算余弦相似度
        similarities = []
        
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                dot_product = sum(
                    a * b for a, b in zip(embeddings[i], embeddings[j])
                )
                norm_i = sum(a * a for a in embeddings[i]) ** 0.5
                norm_j = sum(b * b for b in embeddings[j]) ** 0.5
                
                if norm_i == 0 or norm_j == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_i * norm_j)
                
                similarities.append({
                    "pair": [i, j],
                    "texts": [texts[i], texts[j]],
                    "similarity": similarity,
                })
        
        return ServiceResponse(
            success=True,
            data={
                "total_pairs": len(similarities),
                "similarities": similarities,
                "model": result["model"],
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Calculate similarity failed: {str(e)}",
            error_code="EMBEDDING_SIMILARITY_FAILED",
        )
