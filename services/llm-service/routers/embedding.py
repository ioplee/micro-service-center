from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, LLMException
from services import embedding_service


router = APIRouter()


class EmbeddingRequest(BaseModel):
    input: List[str]
    model: str = "text-embedding-3-small"
    encoding_format: str = "float"
    dimensions: Optional[int] = None
    user: Optional[str] = None


@router.post("/create", tags=["Embedding"], summary="创建文本嵌入")
async def create_embedding(request: EmbeddingRequest):
    try:
        result = embedding_service.create_embedding(
            input_texts=request.input,
            model=request.model,
            encoding_format=request.encoding_format,
            dimensions=request.dimensions,
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
            detail=f"Create embedding failed: {str(e)}",
            error_code="EMBEDDING_CREATE_FAILED",
        )


@router.post("/batch-create", tags=["Embedding"], summary="批量创建文本嵌入")
async def batch_create_embedding(
    inputs: List[List[str]] = Body(...),
    model: str = Body("text-embedding-3-small"),
    batch_size: int = Body(100, ge=1, le=1000),
):
    try:
        all_results = []
        for batch in [inputs[i:i+batch_size] for i in range(0, len(inputs), batch_size)]:
            result = embedding_service.create_embedding(
                input_texts=batch,
                model=model,
            )
            all_results.extend(result.get("data", []))
        
        return ServiceResponse(
            success=True,
            data={
                "data": all_results,
                "total_count": len(all_results),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Batch create embedding failed: {str(e)}",
            error_code="EMBEDDING_BATCH_CREATE_FAILED",
        )


@router.post("/similarity", tags=["Embedding"], summary="计算向量相似度")
async def calculate_similarity(
    vectors1: List[List[float]] = Body(...),
    vectors2: List[List[float]] = Body(...),
    metric: str = Body("cosine"),
):
    try:
        result = embedding_service.calculate_similarity(
            vectors1=vectors1,
            vectors2=vectors2,
            metric=metric,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Calculate similarity failed: {str(e)}",
            error_code="EMBEDDING_SIMILARITY_FAILED",
        )


@router.post("/search", tags=["Embedding"], summary="向量搜索")
async def semantic_search(
    query: str = Body(...),
    documents: List[str] = Body(...),
    top_k: int = Body(5, ge=1, le=100),
    model: str = Body("text-embedding-3-small"),
):
    try:
        result = embedding_service.semantic_search(
            query=query,
            documents=documents,
            top_k=top_k,
            model=model,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Semantic search failed: {str(e)}",
            error_code="EMBEDDING_SEARCH_FAILED",
        )


@router.get("/models", tags=["Embedding"], summary="获取支持的嵌入模型")
async def get_embedding_models():
    try:
        result = embedding_service.get_available_models()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Get embedding models failed: {str(e)}",
            error_code="EMBEDDING_GET_MODELS_FAILED",
        )
