from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, VectorDBException
from services import milvus_service


router = APIRouter()


class CreateCollectionRequest(BaseModel):
    collection_name: str
    dimension: int
    metric_type: str = "L2"
    index_type: str = "IVF_FLAT"
    index_params: Optional[Dict[str, Any]] = None


class InsertRequest(BaseModel):
    collection_name: str
    data: List[List[float]]
    ids: Optional[List[int]] = None


class SearchRequest(BaseModel):
    collection_name: str
    query_vectors: List[List[float]]
    limit: int = 10
    expr: Optional[str] = None
    output_fields: Optional[List[str]] = None


@router.get("/health", tags=["Milvus"], summary="Milvus 健康检查")
async def milvus_health_check():
    try:
        result = milvus_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Milvus health check failed: {str(e)}",
            error_code="MILVUS_HEALTH_CHECK_FAILED",
        )


@router.get("/collections", tags=["Milvus"], summary="获取所有集合")
async def get_collections():
    try:
        result = milvus_service.get_collections()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Failed to get collections: {str(e)}",
            error_code="MILVUS_GET_COLLECTIONS_FAILED",
        )


@router.post("/collections", tags=["Milvus"], summary="创建集合")
async def create_collection(request: CreateCollectionRequest):
    try:
        result = milvus_service.create_collection(
            collection_name=request.collection_name,
            dimension=request.dimension,
            metric_type=request.metric_type,
            index_type=request.index_type,
            index_params=request.index_params,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Create collection failed: {str(e)}",
            error_code="MILVUS_CREATE_COLLECTION_FAILED",
        )


@router.delete("/collections/{collection_name}", tags=["Milvus"], summary="删除集合")
async def delete_collection(collection_name: str):
    try:
        result = milvus_service.delete_collection(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete collection failed: {str(e)}",
            error_code="MILVUS_DELETE_COLLECTION_FAILED",
        )


@router.get("/collections/{collection_name}/info", tags=["Milvus"], summary="获取集合信息")
async def get_collection_info(collection_name: str):
    try:
        result = milvus_service.get_collection_info(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Get collection info failed: {str(e)}",
            error_code="MILVUS_GET_COLLECTION_INFO_FAILED",
        )


@router.post("/collections/{collection_name}/insert", tags=["Milvus"], summary="插入向量")
async def insert(
    collection_name: str,
    data: List[List[float]] = Body(...),
    ids: Optional[List[int]] = Body(None),
):
    try:
        result = milvus_service.insert(collection_name, data, ids)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Insert failed: {str(e)}",
            error_code="MILVUS_INSERT_FAILED",
        )


@router.post("/collections/{collection_name}/search", tags=["Milvus"], summary="向量搜索")
async def search(
    collection_name: str,
    query_vectors: List[List[float]] = Body(...),
    limit: int = Body(10, ge=1, le=1000),
    expr: Optional[str] = Body(None),
    output_fields: Optional[List[str]] = Body(None),
):
    try:
        result = milvus_service.search(
            collection_name,
            query_vectors,
            limit=limit,
            expr=expr,
            output_fields=output_fields,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Search failed: {str(e)}",
            error_code="MILVUS_SEARCH_FAILED",
        )


@router.post("/collections/{collection_name}/query", tags=["Milvus"], summary="查询向量")
async def query(
    collection_name: str,
    expr: str = Body(...),
    output_fields: Optional[List[str]] = Body(None),
    limit: int = Body(100, ge=1),
):
    try:
        result = milvus_service.query(
            collection_name,
            expr=expr,
            output_fields=output_fields,
            limit=limit,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Query failed: {str(e)}",
            error_code="MILVUS_QUERY_FAILED",
        )


@router.delete("/collections/{collection_name}/delete", tags=["Milvus"], summary="删除向量")
async def delete(
    collection_name: str,
    expr: str = Body(...),
):
    try:
        result = milvus_service.delete(collection_name, expr)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete failed: {str(e)}",
            error_code="MILVUS_DELETE_FAILED",
        )


@router.get("/collections/{collection_name}/count", tags=["Milvus"], summary="统计向量数量")
async def count(collection_name: str):
    try:
        result = milvus_service.count(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Count failed: {str(e)}",
            error_code="MILVUS_COUNT_FAILED",
        )


@router.post("/collections/{collection_name}/load", tags=["Milvus"], summary="加载集合到内存")
async def load(collection_name: str):
    try:
        result = milvus_service.load(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Load failed: {str(e)}",
            error_code="MILVUS_LOAD_FAILED",
        )


@router.post("/collections/{collection_name}/release", tags=["Milvus"], summary="释放集合内存")
async def release(collection_name: str):
    try:
        result = milvus_service.release(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Release failed: {str(e)}",
            error_code="MILVUS_RELEASE_FAILED",
        )


@router.post("/collections/{collection_name}/index", tags=["Milvus"], summary="创建索引")
async def create_index(
    collection_name: str,
    index_type: str = Body("IVF_FLAT"),
    index_params: Optional[Dict[str, Any]] = Body(None),
):
    try:
        result = milvus_service.create_index(
            collection_name,
            index_type=index_type,
            index_params=index_params,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Create index failed: {str(e)}",
            error_code="MILVUS_CREATE_INDEX_FAILED",
        )


@router.delete("/collections/{collection_name}/index", tags=["Milvus"], summary="删除索引")
async def drop_index(collection_name: str):
    try:
        result = milvus_service.drop_index(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Drop index failed: {str(e)}",
            error_code="MILVUS_DROP_INDEX_FAILED",
        )
