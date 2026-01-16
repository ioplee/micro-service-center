from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, DatabaseException
from services import mysql_service


router = APIRouter()


class QueryRequest(BaseModel):
    sql: str
    params: Optional[Dict[str, Any]] = None


class InsertRequest(BaseModel):
    table: str
    data: Dict[str, Any]
    

class UpdateRequest(BaseModel):
    table: str
    data: Dict[str, Any]
    where: Optional[Dict[str, Any]] = None
    

class DeleteRequest(BaseModel):
    table: str
    where: Optional[Dict[str, Any]] = None


class BulkInsertRequest(BaseModel):
    table: str
    data: List[Dict[str, Any]]
    batch_size: int = 1000


@router.get("/health", tags=["MySQL"], summary="MySQL 健康检查")
async def mysql_health_check():
    try:
        result = mysql_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"MySQL health check failed: {str(e)}",
            error_code="MYSQL_HEALTH_CHECK_FAILED",
        )


@router.get("/tables", tags=["MySQL"], summary="获取所有表")
async def get_tables():
    try:
        result = mysql_service.get_tables()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Failed to get tables: {str(e)}",
            error_code="MYSQL_GET_TABLES_FAILED",
        )


@router.get("/tables/{table_name}/schema", tags=["MySQL"], summary="获取表结构")
async def get_table_schema(table_name: str):
    try:
        result = mysql_service.get_table_schema(table_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Failed to get table schema: {str(e)}",
            error_code="MYSQL_GET_SCHEMA_FAILED",
        )


@router.post("/query", tags=["MySQL"], summary="执行查询")
async def execute_query(request: QueryRequest):
    try:
        result = mysql_service.execute_query(request.sql, request.params)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Query execution failed: {str(e)}",
            error_code="MYSQL_QUERY_FAILED",
        )


@router.post("/execute", tags=["MySQL"], summary="执行 SQL（无返回结果）")
async def execute_sql(request: QueryRequest):
    try:
        result = mysql_service.execute_sql(request.sql, request.params)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"SQL execution failed: {str(e)}",
            error_code="MYSQL_EXECUTE_FAILED",
        )


@router.post("/insert", tags=["MySQL"], summary="插入单条数据")
async def insert(request: InsertRequest):
    try:
        result = mysql_service.insert(request.table, request.data)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Insert failed: {str(e)}",
            error_code="MYSQL_INSERT_FAILED",
        )


@router.post("/insert/bulk", tags=["MySQL"], summary="批量插入数据")
async def bulk_insert(request: BulkInsertRequest):
    try:
        result = mysql_service.bulk_insert(
            request.table,
            request.data,
            request.batch_size
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Bulk insert failed: {str(e)}",
            error_code="MYSQL_BULK_INSERT_FAILED",
        )


@router.put("/update", tags=["MySQL"], summary="更新数据")
async def update(request: UpdateRequest):
    try:
        result = mysql_service.update(
            request.table,
            request.data,
            request.where
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
            error_code="MYSQL_UPDATE_FAILED",
        )


@router.delete("/delete", tags=["MySQL"], summary="删除数据")
async def delete(request: DeleteRequest):
    try:
        result = mysql_service.delete(
            request.table,
            request.where
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
            error_code="MYSQL_DELETE_FAILED",
        )


@router.get("/select/{table_name}", tags=["MySQL"], summary="查询数据")
async def select(
    table_name: str,
    fields: Optional[List[str]] = Query(None),
    where: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=10000),
    offset: int = Query(0, ge=0),
    order_by: Optional[str] = Query(None),
):
    try:
        result = mysql_service.select(
            table_name,
            fields=fields,
            where=where,
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise DatabaseException(
            detail=f"Select failed: {str(e)}",
            error_code="MYSQL_SELECT_FAILED",
        )
