from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, DatabaseException
from services import mongodb_service


router = APIRouter()


class FindRequest(BaseModel):
    collection: str
    filter: Optional[Dict[str, Any]] = None
    projection: Optional[Dict[str, Any]] = None
    limit: int = 100
    skip: int = 0
    sort: Optional[List[List]] = None


class InsertRequest(BaseModel):
    collection: str
    data: Dict[str, Any]
    

class InsertManyRequest(BaseModel):
    collection: str
    data: List[Dict[str, Any]]
    

class UpdateRequest(BaseModel):
    collection: str
    filter: Dict[str, Any]
    data: Dict[str, Any]
    upsert: bool = False
    multi: bool = False
    

class DeleteRequest(BaseModel):
    collection: str
    filter: Dict[str, Any]
    multi: bool = False


class AggregateRequest(BaseModel):
    collection: str
    pipeline: List[Dict[str, Any]]
    

@router.get("/health", tags=["MongoDB"], summary="MongoDB 健康检查")
async def mongodb_health_check():
    try:
        result = mongodb_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"MongoDB health check failed: {str(e)}",
            error_code="MONGODB_HEALTH_CHECK_FAILED",
        )


@router.get("/collections", tags=["MongoDB"], summary="获取所有集合")
async def get_collections():
    try:
        result = mongodb_service.get_collections()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Failed to get collections: {str(e)}",
            error_code="MONGODB_GET_COLLECTIONS_FAILED",
        )


@router.post("/find", tags=["MongoDB"], summary="查询文档")
async def find(request: FindRequest):
    try:
        result = mongodb_service.find(
            request.collection,
            filter=request.filter,
            projection=request.projection,
            limit=request.limit,
            skip=request.skip,
            sort=request.sort
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Find failed: {str(e)}",
            error_code="MONGODB_FIND_FAILED",
        )


@router.post("/find_one", tags=["MongoDB"], summary="查询单个文档")
async def find_one(
    collection: str,
    filter: Optional[Dict[str, Any]] = Body(None),
    projection: Optional[Dict[str, Any]] = Body(None),
):
    try:
        result = mongodb_service.find_one(
            collection,
            filter=filter,
            projection=projection
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Find one failed: {str(e)}",
            error_code="MONGODB_FIND_ONE_FAILED",
        )


@router.post("/insert", tags=["MongoDB"], summary="插入单个文档")
async def insert(request: InsertRequest):
    try:
        result = mongodb_service.insert(request.collection, request.data)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Insert failed: {str(e)}",
            error_code="MONGODB_INSERT_FAILED",
        )


@router.post("/insert_many", tags=["MongoDB"], summary="批量插入文档")
async def insert_many(request: InsertManyRequest):
    try:
        result = mongodb_service.insert_many(request.collection, request.data)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Insert many failed: {str(e)}",
            error_code="MONGODB_INSERT_MANY_FAILED",
        )


@router.put("/update", tags=["MongoDB"], summary="更新文档")
async def update(request: UpdateRequest):
    try:
        result = mongodb_service.update(
            request.collection,
            request.filter,
            request.data,
            upsert=request.upsert,
            multi=request.multi
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Update failed: {str(e)}",
            error_code="MONGODB_UPDATE_FAILED",
        )


@router.delete("/delete", tags=["MongoDB"], summary="删除文档")
async def delete(request: DeleteRequest):
    try:
        result = mongodb_service.delete(
            request.collection,
            request.filter,
            multi=request.multi
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Delete failed: {str(e)}",
            error_code="MONGODB_DELETE_FAILED",
        )


@router.post("/aggregate", tags=["MongoDB"], summary="聚合查询")
async def aggregate(request: AggregateRequest):
    try:
        result = mongodb_service.aggregate(
            request.collection,
            request.pipeline
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Aggregate failed: {str(e)}",
            error_code="MONGODB_AGGREGATE_FAILED",
        )


@router.get("/count", tags=["MongoDB"], summary="统计文档数量")
async def count(
    collection: str,
    filter: Optional[Dict[str, Any]] = Query(None),
):
    try:
        result = mongodb_service.count(collection, filter=filter)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Count failed: {str(e)}",
            error_code="MONGODB_COUNT_FAILED",
        )


@router.delete("/drop_collection", tags=["MongoDB"], summary="删除集合")
async def drop_collection(collection: str):
    try:
        result = mongodb_service.drop_collection(collection)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Drop collection failed: {str(e)}",
            error_code="MONGODB_DROP_COLLECTION_FAILED",
        )
