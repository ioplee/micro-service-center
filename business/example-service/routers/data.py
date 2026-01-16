from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time
import httpx

from common import ServiceResponse


router = APIRouter()


DATABASE_SERVICE = "http://localhost:8001"


class CreateDocumentRequest(BaseModel):
    collection_name: str
    document: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentSearchRequest(BaseModel):
    collection_name: str
    query: str
    limit: int = 10
    offset: int = 0


@router.post("/documents", tags=["Data"], summary="创建文档")
async def create_document(request: CreateDocumentRequest):
    try:
        # 1. 存储到 MongoDB
        async with httpx.AsyncClient() as client:
            mongo_response = await client.post(
                f"{DATABASE_SERVICE}/mongodb/insert",
                json={
                    "collection": request.collection_name,
                    "data": {
                        "content": request.document,
                        "metadata": request.metadata or {},
                        "created_at": time.time(),
                        "updated_at": time.time(),
                    },
                },
            )
            mongo_response.raise_for_status()
            mongo_data = mongo_response.json()
        
        return ServiceResponse(
            success=True,
            data={
                "status": "success",
                "message": "文档已创建",
                "inserted_id": mongo_data["data"].get("inserted_id"),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Create document failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.get("/documents/{collection_name}", tags=["Data"], summary="获取文档列表")
async def get_documents(
    collection_name: str,
    limit: int = Query(10, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort: Optional[str] = Query(None),
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATABASE_SERVICE}/mongodb/find",
                json={
                    "collection": collection_name,
                    "filter": {},
                    "limit": limit,
                    "skip": offset,
                    "sort": [[sort, -1]] if sort else None,
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data=response_data["data"],
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Get documents failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.get("/documents/{collection_name}/{document_id}", tags=["Data"], summary="获取单个文档")
async def get_document(collection_name: str, document_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATABASE_SERVICE}/mongodb/find_one",
                json={
                    "collection": collection_name,
                    "filter": {"_id": document_id},
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data=response_data["data"],
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Get document failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.put("/documents/{collection_name}/{document_id}", tags=["Data"], summary="更新文档")
async def update_document(
    collection_name: str,
    document_id: str,
    content: Optional[str] = Body(None),
    metadata: Optional[Dict[str, Any]] = Body(None),
):
    try:
        update_data = {"updated_at": time.time()}
        if content:
            update_data["content"] = content
        if metadata:
            update_data["metadata"] = metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{DATABASE_SERVICE}/mongodb/update",
                json={
                    "collection": collection_name,
                    "filter": {"_id": document_id},
                    "data": {"$set": update_data},
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data={
                "status": "success",
                "message": "文档已更新",
                "matched_count": response_data["data"].get("matched_count"),
                "modified_count": response_data["data"].get("modified_count"),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Update document failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.delete("/documents/{collection_name}/{document_id}", tags=["Data"], summary="删除文档")
async def delete_document(collection_name: str, document_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{DATABASE_SERVICE}/mongodb/delete",
                json={
                    "collection": collection_name,
                    "filter": {"_id": document_id},
                },
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data={
                "status": "success",
                "message": "文档已删除",
                "deleted_count": response_data["data"].get("deleted_count"),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Delete document failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.get("/documents/{collection_name}/count", tags=["Data"], summary="统计文档数量")
async def count_documents(collection_name: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATABASE_SERVICE}/mongodb/count",
                params={"collection": collection_name},
            )
            response.raise_for_status()
            response_data = response.json()
        
        return ServiceResponse(
            success=True,
            data={
                "collection_name": collection_name,
                "count": response_data["data"],
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Count documents failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )
