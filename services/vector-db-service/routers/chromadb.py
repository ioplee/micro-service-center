from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, VectorDBException
from services import chromadb_service


router = APIRouter()


class CreateCollectionRequest(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None


class AddDocumentsRequest(BaseModel):
    collection_name: str
    documents: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    ids: Optional[List[str]] = None
    embeddings: Optional[List[List[float]]] = None


class QueryRequest(BaseModel):
    collection_name: str
    query_texts: List[str]
    n_results: int = 10
    where: Optional[Dict[str, Any]] = None
    where_document: Optional[Dict[str, Any]] = None
    include: Optional[List[str]] = None


@router.get("/health", tags=["ChromaDB"], summary="ChromaDB 健康检查")
async def chromadb_health_check():
    try:
        result = chromadb_service.health_check()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"ChromaDB health check failed: {str(e)}",
            error_code="CHROMADB_HEALTH_CHECK_FAILED",
        )


@router.get("/collections", tags=["ChromaDB"], summary="获取所有集合")
async def get_collections():
    try:
        result = chromadb_service.get_collections()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Failed to get collections: {str(e)}",
            error_code="CHROMADB_GET_COLLECTIONS_FAILED",
        )


@router.post("/collections", tags=["ChromaDB"], summary="创建集合")
async def create_collection(request: CreateCollectionRequest):
    try:
        result = chromadb_service.create_collection(
            name=request.name,
            metadata=request.metadata,
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
            error_code="CHROMADB_CREATE_COLLECTION_FAILED",
        )


@router.delete("/collections/{collection_name}", tags=["ChromaDB"], summary="删除集合")
async def delete_collection(collection_name: str):
    try:
        result = chromadb_service.delete_collection(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete collection failed: {str(e)}",
            error_code="CHROMADB_DELETE_COLLECTION_FAILED",
        )


@router.get("/collections/{collection_name}", tags=["ChromaDB"], summary="获取集合")
async def get_collection(collection_name: str):
    try:
        result = chromadb_service.get_collection(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Get collection failed: {str(e)}",
            error_code="CHROMADB_GET_COLLECTION_FAILED",
        )


@router.post("/collections/{collection_name}/add", tags=["ChromaDB"], summary="添加文档")
async def add(
    collection_name: str,
    documents: List[str] = Body(...),
    metadatas: Optional[List[Dict[str, Any]]] = Body(None),
    ids: Optional[List[str]] = Body(None),
    embeddings: Optional[List[List[float]]] = Body(None),
):
    try:
        result = chromadb_service.add(
            collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Add documents failed: {str(e)}",
            error_code="CHROMADB_ADD_DOCUMENTS_FAILED",
        )


@router.post("/collections/{collection_name}/query", tags=["ChromaDB"], summary="查询文档")
async def query(
    collection_name: str,
    query_texts: List[str] = Body(...),
    n_results: int = Body(10, ge=1, le=1000),
    where: Optional[Dict[str, Any]] = Body(None),
    where_document: Optional[Dict[str, Any]] = Body(None),
    include: Optional[List[str]] = Body(None),
):
    try:
        result = chromadb_service.query(
            collection_name,
            query_texts=query_texts,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include,
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
            error_code="CHROMADB_QUERY_FAILED",
        )


@router.post("/collections/{collection_name}/get", tags=["ChromaDB"], summary="获取文档")
async def get(
    collection_name: str,
    ids: Optional[List[str]] = Body(None),
    where: Optional[Dict[str, Any]] = Body(None),
    where_document: Optional[Dict[str, Any]] = Body(None),
    include: Optional[List[str]] = Body(None),
    limit: Optional[int] = Body(None),
):
    try:
        result = chromadb_service.get(
            collection_name,
            ids=ids,
            where=where,
            where_document=where_document,
            include=include,
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
            detail=f"Get documents failed: {str(e)}",
            error_code="CHROMADB_GET_DOCUMENTS_FAILED",
        )


@router.post("/collections/{collection_name}/update", tags=["ChromaDB"], summary="更新文档")
async def update(
    collection_name: str,
    ids: List[str] = Body(...),
    documents: Optional[List[str]] = Body(None),
    metadatas: Optional[List[Dict[str, Any]]] = Body(None),
    embeddings: Optional[List[List[float]]] = Body(None),
):
    try:
        result = chromadb_service.update(
            collection_name,
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Update failed: {str(e)}",
            error_code="CHROMADB_UPDATE_FAILED",
        )


@router.post("/collections/{collection_name}/upsert", tags=["ChromaDB"], summary="插入或更新文档")
async def upsert(
    collection_name: str,
    documents: List[str] = Body(...),
    metadatas: Optional[List[Dict[str, Any]]] = Body(None),
    ids: Optional[List[str]] = Body(None),
    embeddings: Optional[List[List[float]]] = Body(None),
):
    try:
        result = chromadb_service.upsert(
            collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Upsert failed: {str(e)}",
            error_code="CHROMADB_UPSERT_FAILED",
        )


@router.post("/collections/{collection_name}/delete", tags=["ChromaDB"], summary="删除文档")
async def delete(
    collection_name: str,
    ids: Optional[List[str]] = Body(None),
    where: Optional[Dict[str, Any]] = Body(None),
    where_document: Optional[Dict[str, Any]] = Body(None),
):
    try:
        result = chromadb_service.delete(
            collection_name,
            ids=ids,
            where=where,
            where_document=where_document,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Delete failed: {str(e)}",
            error_code="CHROMADB_DELETE_FAILED",
        )


@router.get("/collections/{collection_name}/count", tags=["ChromaDB"], summary="统计文档数量")
async def count(collection_name: str):
    try:
        result = chromadb_service.count(collection_name)
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Count failed: {str(e)}",
            error_code="CHROMADB_COUNT_FAILED",
        )


@router.post("/collections/{collection_name}/modify", tags=["ChromaDB"], summary="修改集合")
async def modify(
    collection_name: str,
    name: Optional[str] = Body(None),
    metadata: Optional[Dict[str, Any]] = Body(None),
):
    try:
        result = chromadb_service.modify(
            collection_name,
            name=name,
            metadata=metadata,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise VectorDBException(
            detail=f"Modify failed: {str(e)}",
            error_code="CHROMADB_MODIFY_FAILED",
        )
