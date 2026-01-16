from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, DatabaseException
from services import redis_service


router = APIRouter()


class SetRequest(BaseModel):
    key: str
    value: Any
    expire: Optional[int] = None


class GetRequest(BaseModel):
    key: str


class DeleteRequest(BaseModel):
    keys: List[str]


class SetMultipleRequest(BaseModel):
    data: Dict[str, Any]
    expire: Optional[int] = None


class HashSetRequest(BaseModel):
    key: str
    field: str
    value: Any


class HashGetRequest(BaseModel):
    key: str
    field: Optional[str] = None


class ListPushRequest(BaseModel):
    key: str
    values: List[Any]
    position: str = "right"  # "left" or "right"


class ListPopRequest(BaseModel):
    key: str
    position: str = "right"
    count: int = 1


class ZAddRequest(BaseModel):
    key: str
    members: Dict[str, float]


class ZRangeRequest(BaseModel):
    key: str
    start: int = 0
    end: int = -1
    with_scores: bool = False


@router.get("/health", tags=["Redis"], summary="Redis 健康检查")
async def redis_health_check():
    try:
        result = redis_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Redis health check failed: {str(e)}",
            error_code="REDIS_HEALTH_CHECK_FAILED",
        )


@router.get("/info", tags=["Redis"], summary="获取 Redis 信息")
async def get_redis_info():
    try:
        result = redis_service.get_info()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Failed to get Redis info: {str(e)}",
            error_code="REDIS_GET_INFO_FAILED",
        )


@router.post("/set", tags=["Redis"], summary="设置键值对")
async def set_key(request: SetRequest):
    try:
        result = redis_service.set(
            request.key,
            request.value,
            expire=request.expire
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Set failed: {str(e)}",
            error_code="REDIS_SET_FAILED",
        )


@router.get("/get/{key}", tags=["Redis"], summary="获取键值")
async def get_key(key: str):
    try:
        result = redis_service.get(key)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Get failed: {str(e)}",
            error_code="REDIS_GET_FAILED",
        )


@router.post("/set_multiple", tags=["Redis"], summary="批量设置键值对")
async def set_multiple(request: SetMultipleRequest):
    try:
        result = redis_service.set_multiple(
            request.data,
            expire=request.expire
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Set multiple failed: {str(e)}",
            error_code="REDIS_SET_MULTIPLE_FAILED",
        )


@router.post("/get_multiple", tags=["Redis"], summary="批量获取键值")
async def get_multiple(keys: List[str] = Body(...)):
    try:
        result = redis_service.get_multiple(keys)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Get multiple failed: {str(e)}",
            error_code="REDIS_GET_MULTIPLE_FAILED",
        )


@router.delete("/delete", tags=["Redis"], summary="删除键")
async def delete_keys(request: DeleteRequest):
    try:
        result = redis_service.delete(request.keys)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Delete failed: {str(e)}",
            error_code="REDIS_DELETE_FAILED",
        )


@router.get("/exists/{key}", tags=["Redis"], summary="检查键是否存在")
async def exists(key: str):
    try:
        result = redis_service.exists(key)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Exists check failed: {str(e)}",
            error_code="REDIS_EXISTS_FAILED",
        )


@router.post("/expire", tags=["Redis"], summary="设置键过期时间")
async def expire(
    key: str = Body(...),
    seconds: int = Body(...),
):
    try:
        result = redis_service.expire(key, seconds)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Expire failed: {str(e)}",
            error_code="REDIS_EXPIRE_FAILED",
        )


@router.get("/ttl/{key}", tags=["Redis"], summary="获取键剩余过期时间")
async def ttl(key: str):
    try:
        result = redis_service.ttl(key)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"TTL check failed: {str(e)}",
            error_code="REDIS_TTL_FAILED",
        )


# Hash 操作
@router.post("/hset", tags=["Redis Hash"], summary="设置哈希字段")
async def hset(request: HashSetRequest):
    try:
        result = redis_service.hset(request.key, request.field, request.value)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"HSet failed: {str(e)}",
            error_code="REDIS_HSET_FAILED",
        )


@router.get("/hget/{key}", tags=["Redis Hash"], summary="获取哈希字段")
async def hget(
    key: str,
    field: Optional[str] = Query(None),
):
    try:
        result = redis_service.hget(key, field)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"HGet failed: {str(e)}",
            error_code="REDIS_HGET_FAILED",
        )


@router.post("/hmset", tags=["Redis Hash"], summary="批量设置哈希字段")
async def hmset(
    key: str = Body(...),
    data: Dict[str, Any] = Body(...),
):
    try:
        result = redis_service.hmset(key, data)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"HMSet failed: {str(e)}",
            error_code="REDIS_HMSET_FAILED",
        )


# List 操作
@router.post("/lpush", tags=["Redis List"], summary="左侧插入列表")
async def lpush(
    key: str = Body(...),
    values: List[Any] = Body(...),
):
    try:
        result = redis_service.lpush(key, values)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"LPush failed: {str(e)}",
            error_code="REDIS_LPUSH_FAILED",
        )


@router.post("/rpush", tags=["Redis List"], summary="右侧插入列表")
async def rpush(
    key: str = Body(...),
    values: List[Any] = Body(...),
):
    try:
        result = redis_service.rpush(key, values)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"RPush failed: {str(e)}",
            error_code="REDIS_RPUSH_FAILED",
        )


@router.get("/lpop/{key}", tags=["Redis List"], summary="左侧弹出列表")
async def lpop(
    key: str,
    count: int = Query(1, ge=1),
):
    try:
        result = redis_service.lpop(key, count)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"LPop failed: {str(e)}",
            error_code="REDIS_LPOP_FAILED",
        )


@router.get("/rpop/{key}", tags=["Redis List"], summary="右侧弹出列表")
async def rpop(
    key: str,
    count: int = Query(1, ge=1),
):
    try:
        result = redis_service.rpop(key, count)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"RPop failed: {str(e)}",
            error_code="REDIS_RPOP_FAILED",
        )


# Set 操作
@router.post("/sadd", tags=["Redis Set"], summary="添加集合元素")
async def sadd(
    key: str = Body(...),
    values: List[Any] = Body(...),
):
    try:
        result = redis_service.sadd(key, values)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"SAdd failed: {str(e)}",
            error_code="REDIS_SADD_FAILED",
        )


@router.get("/smembers/{key}", tags=["Redis Set"], summary="获取集合所有元素")
async def smembers(key: str):
    try:
        result = redis_service.smembers(key)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"SMembers failed: {str(e)}",
            error_code="REDIS_SMEMBERS_FAILED",
        )


# Sorted Set 操作
@router.post("/zadd", tags=["Redis Sorted Set"], summary="添加有序集合元素")
async def zadd(request: ZAddRequest):
    try:
        result = redis_service.zadd(request.key, request.members)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"ZAdd failed: {str(e)}",
            error_code="REDIS_ZADD_FAILED",
        )


@router.get("/zrange/{key}", tags=["Redis Sorted Set"], summary="获取有序集合范围")
async def zrange(
    key: str,
    start: int = Query(0),
    end: int = Query(-1),
    with_scores: bool = Query(False),
):
    try:
        result = redis_service.zrange(key, start, end, with_scores)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"ZRange failed: {str(e)}",
            error_code="REDIS_ZRANGE_FAILED",
        )


# 发布订阅
@router.post("/publish", tags=["Redis Pub/Sub"], summary="发布消息")
async def publish(
    channel: str = Body(...),
    message: Any = Body(...),
):
    try:
        result = redis_service.publish(channel, message)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Publish failed: {str(e)}",
            error_code="REDIS_PUBLISH_FAILED",
        )


# 事务
@router.post("/transaction", tags=["Redis Transaction"], summary="执行事务")
async def transaction(
    commands: List[List[str]] = Body(...),
):
    try:
        result = redis_service.transaction(commands)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Transaction failed: {str(e)}",
            error_code="REDIS_TRANSACTION_FAILED",
        )


# Lua 脚本
@router.post("/eval", tags=["Redis Scripting"], summary="执行 Lua 脚本")
async def eval(
    script: str = Body(...),
    keys: List[str] = Body(default_factory=list),
    args: List[Any] = Body(default_factory=list),
):
    try:
        result = redis_service.eval(script, keys, args)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Eval failed: {str(e)}",
            error_code="REDIS_EVAL_FAILED",
        )
