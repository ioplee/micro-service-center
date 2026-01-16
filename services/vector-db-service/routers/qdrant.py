from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, VectorDBException
from services import qdrant_service


router = APIRouter()


class CreateCollectionRequest(BaseModel):
    collection_name: str
    vector_size: int
    distance: str = "Cosine"
    shard_number: Optional[int] = None
    replication_factor: Optional[int] = None


class InsertRequest(BaseModel):
    collection_name: str
    points: List[Dict[str, Any]]


class SearchRequest(BaseModel):
    collection_name: str
    query_vector: List[float]
    limit: int = 10
    offset: int = 0
    filter: Optional[Dict[str, Any]] = None
    with_payload: bool = True
    with_vectors: bool = False


class QueryRequest(BaseModel):
    collection_name: str
    query: str
    limit: int = 10
    offset: int = 0
    filter: Optional[Dict[str, Any]] = None


@router.get("/health", tags=["Qdrant"], summary="Qdrant 健康检查")
async def qdrant_health_check():
    try:
        result = qdrant_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Qdrant health check failed: {str(e)}",
            error_code="QDRANT_HEALTH_CHECK_FAILED",
        )


@router.get("/collections", tags=["Qdrant"], summary="获取所有集合")
async def get_collections():
    try:
        result = qdrant_service.get_collections()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Failed to get collections: {str(e)}",
            error_code="QDRANT_GET_COLLECTIONS_FAILED",
        )


@router.post("/collections", tags=["Qdrant"], summary="创建集合")
async def create_collection(request: CreateCollectionRequest):
    try:
        result = qdrant_service.create_collection(
            collection_name=request.collection_name,
            vector_size=request.vector_size,
            distance=request.distance,
            shard_number=request.shard_number,
            replication_factor=request.replication_factor,
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
            error_code="QDRANT_CREATE_COLLECTION_FAILED",
        )


@router.delete("/collections/{collection_name}", tags=["Qdrant"], summary="删除集合")
async def delete_collection(collection_name: str):
    try:
        result = qdrant_service.delete_collection(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete collection failed: {str(e)}",
            error_code="QDRANT_DELETE_COLLECTION_FAILED",
        )


@router.get("/collections/{collection_name}/info", tags=["Qdrant"], summary="获取集合信息")
async def get_collection_info(collection_name: str):
    try:
        result = qdrant_service.get_collection_info(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Get collection info failed: {str(e)}",
            error_code="QDRANT_GET_COLLECTION_INFO_FAILED",
        )


@router.post("/collections/{collection_name}/points", tags=["Qdrant"], summary="插入向量点")
async def insert_points(
    collection_name: str,
    points: List[Dict[str, Any]] = Body(...),
):
    try:
        result = qdrant_service.insert_points(collection_name, points)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Insert points failed: {str(e)}",
            error_code="QDRANT_INSERT_POINTS_FAILED",
        )


@router.post("/collections/{collection_name}/search", tags=["Qdrant"], summary="向量搜索")
async def search(
    collection_name: str,
    query_vector: List[float] = Body(...),
    limit: int = Body(10, ge=1, le=1000),
    offset: int = Body(0, ge=0),
    filter: Optional[Dict[str, Any]] = Body(None),
    with_payload: bool = Body(True),
    with_vectors: bool = Body(False),
):
    try:
        result = qdrant_service.search(
            collection_name,
            query_vector,
            limit=limit,
            offset=offset,
            filter=filter,
            with_payload=with_payload,
            with_vectors=with_vectors,
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
            error_code="QDRANT_SEARCH_FAILED",
        )


@router.post("/collections/{collection_name}/query", tags=["Qdrant"], summary="向量查询")
async def query(
    collection_name: str,
    query: str = Body(...),
    limit: int = Body(10, ge=1, le=1000),
    offset: int = Body(0, ge=0),
    filter: Optional[Dict[str, Any]] = Body(None),
):
    try:
        result = qdrant_service.query(
            collection_name,
            query,
            limit=limit,
            offset=offset,
            filter=filter,
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
            error_code="QDRANT_QUERY_FAILED",
        )


@router.get("/collections/{collection_name}/points/{point_id}", tags=["Qdrant"], summary="获取向量点")
async def get_point(
    collection_name: str,
    point_id: int,
    with_payload: bool = Query(True),
    with_vector: bool = Query(False),
):
    try:
        result = qdrant_service.get_point(
            collection_name,
            point_id,
            with_payload=with_payload,
            with_vector=with_vector,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Get point failed: {str(e)}",
            error_code="QDRANT_GET_POINT_FAILED",
        )


@router.put("/collections/{collection_name}/points/{point_id}", tags=["Qdrant"], summary="更新向量点")
async def update_point(
    collection_name: str,
    point_id: int,
    payload: Optional[Dict[str, Any]] = Body(None),
    vector: Optional[List[float]] = Body(None),
):
    try:
        result = qdrant_service.update_point(
            collection_name,
            point_id,
            payload=payload,
            vector=vector,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Update point failed: {str(e)}",
            error_code="QDRANT_UPDATE_POINT_FAILED",
        )


@router.delete("/collections/{collection_name}/points/{point_id}", tags=["Qdrant"], summary="删除向量点")
async def delete_point(
    collection_name: str,
    point_id: int,
):
    try:
        result = qdrant_service.delete_point(collection_name, point_id)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete point failed: {str(e)}",
            error_code="QDRANT_DELETE_POINT_FAILED",
        )


@router.delete("/collections/{collection_name}/points", tags=["Qdrant"], summary="批量删除向量点")
async def delete_points(
    collection_name: str,
    point_ids: List[int] = Body(...),
):
    try:
        result = qdrant_service.delete_points(collection_name, point_ids)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete points failed: {str(e)}",
            error_code="QDRANT_DELETE_POINTS_FAILED",
        )


@router.post("/collections/{collection_name}/scroll", tags=["Qdrant"], summary="滚动查询")
async def scroll(
    collection_name: str,
    limit: int = Body(100, ge=1, le=10000),
    offset: Optional[str] = Body(None),
    filter: Optional[Dict[str, Any]] = Body(None),
    with_payload: bool = Body(True),
    with_vectors: bool = Body(False),
):
    try:
        result = qdrant_service.scroll(
            collection_name,
            limit=limit,
            offset=offset,
            filter=filter,
            with_payload=with_payload,
            with_vectors=with_vectors,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Scroll failed: {str(e)}",
            error_code="QDRANT_SCROLL_FAILED",
        )


@router.post("/collections/{collection_name}/alias", tags=["Qdrant"], summary="设置集合别名")
async def set_alias(
    collection_name: str,
    alias_name: str = Body(...),
):
    try:
        result = qdrant_service.set_alias(collection_name, alias_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Set alias failed: {str(e)}",
            error_code="QDRANT_SET_ALIAS_FAILED",
        )


@router.delete("/collections/alias/{alias_name}", tags=["Qdrant"], summary="删除集合别名")
async def delete_alias(alias_name: str):
    try:
        result = qdrant_service.delete_alias(alias_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete alias failed: {str(e)}",
            error_code="QDRANT_DELETE_ALIAS_FAILED",
        )
