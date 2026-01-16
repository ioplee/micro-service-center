from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time
import httpx

from common import ServiceResponse


router = APIRouter()


# 基础服务配置
VECTOR_DB_SERVICE = "http://localhost:8002"
LLM_SERVICE = "http://localhost:8003"


class SemanticSearchRequest(BaseModel):
    query: str
    collection_name: str = "documents"
    top_k: int = 10
    with_payload: bool = True


class HybridSearchRequest(BaseModel):
    query: str
    collection_name: str = "documents"
    top_k: int = 10
    semantic_weight: float = 0.7
    keyword_weight: float = 0.3


@router.post("/semantic", tags=["Search"], summary="语义搜索")
async def semantic_search(request: SemanticSearchRequest):
    try:
        # 1. 创建查询嵌入
        async with httpx.AsyncClient() as client:
            embedding_response = await client.post(
                f"{LLM_SERVICE}/embedding/create",
                json={
                    "input": [request.query],
                    "model": "text-embedding-3-small",
                },
            )
            embedding_response.raise_for_status()
            embedding_data = embedding_response.json()
            
            query_vector = embedding_data["data"][0]["embedding"]
        
        # 2. 向量搜索
        async with httpx.AsyncClient() as client:
            search_response = await client.post(
                f"{VECTOR_DB_SERVICE}/qdrant/collections/{request.collection_name}/search",
                json={
                    "query_vector": query_vector,
                    "limit": request.top_k,
                    "with_payload": request.with_payload,
                },
            )
            search_response.raise_for_status()
            search_results = search_response.json()
        
        return ServiceResponse(
            success=True,
            data={
                "query": request.query,
                "results": search_results,
                "total_count": len(search_results),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Semantic search failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.post("/hybrid", tags=["Search"], summary="混合搜索")
async def hybrid_search(request: HybridSearchRequest):
    try:
        # 1. 语义搜索
        async with httpx.AsyncClient() as client:
            embedding_response = await client.post(
                f"{LLM_SERVICE}/embedding/create",
                json={
                    "input": [request.query],
                    "model": "text-embedding-3-small",
                },
            )
            embedding_response.raise_for_status()
            embedding_data = embedding_response.json()
            
            query_vector = embedding_data["data"][0]["embedding"]
        
        async with httpx.AsyncClient() as client:
            semantic_response = await client.post(
                f"{VECTOR_DB_SERVICE}/qdrant/collections/{request.collection_name}/search",
                json={
                    "query_vector": query_vector,
                    "limit": request.top_k,
                    "with_payload": True,
                },
            )
            semantic_response.raise_for_status()
            semantic_results = semantic_response.json()
        
        # 2. 关键词搜索（使用 Qdrant 的查询能力）
        async with httpx.AsyncClient() as client:
            keyword_response = await client.post(
                f"{VECTOR_DB_SERVICE}/qdrant/collections/{request.collection_name}/query",
                json={
                    "query": request.query,
                    "limit": request.top_k,
                },
            )
            keyword_response.raise_for_status()
            keyword_results = keyword_response.json()
        
        # 3. 融合结果
        merged_results = {}
        
        for result in semantic_results:
            doc_id = str(result.get("id", ""))
            if doc_id not in merged_results:
                merged_results[doc_id] = {
                    "id": result.get("id"),
                    "payload": result.get("payload"),
                    "semantic_score": result.get("score", 0),
                    "keyword_score": 0,
                }
            else:
                merged_results[doc_id]["semantic_score"] = result.get("score", 0)
        
        for result in keyword_results:
            doc_id = str(result.get("id", ""))
            if doc_id not in merged_results:
                merged_results[doc_id] = {
                    "id": result.get("id"),
                    "payload": result.get("payload"),
                    "semantic_score": 0,
                    "keyword_score": result.get("score", 0),
                }
            else:
                merged_results[doc_id]["keyword_score"] = result.get("score", 0)
        
        # 计算综合得分
        for doc_id, data in merged_results.items():
            data["total_score"] = (
                data["semantic_score"] * request.semantic_weight +
                data["keyword_score"] * request.keyword_weight
            )
        
        # 排序
        final_results = sorted(
            merged_results.values(),
            key=lambda x: x["total_score"],
            reverse=True
        )[:request.top_k]
        
        return ServiceResponse(
            success=True,
            data={
                "query": request.query,
                "results": final_results,
                "total_count": len(final_results),
                "semantic_weight": request.semantic_weight,
                "keyword_weight": request.keyword_weight,
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"Hybrid search failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )


@router.post("/rag", tags=["Search"], summary="RAG 搜索")
async def rag_search(
    query: str = Body(...),
    collection_name: str = Body("documents"),
    top_k: int = Body(5),
    max_tokens: int = Body(1000),
):
    try:
        # 1. 语义搜索获取相关文档
        async with httpx.AsyncClient() as client:
            embedding_response = await client.post(
                f"{LLM_SERVICE}/embedding/create",
                json={
                    "input": [query],
                    "model": "text-embedding-3-small",
                },
            )
            embedding_response.raise_for_status()
            embedding_data = embedding_response.json()
            
            query_vector = embedding_data["data"][0]["embedding"]
        
        async with httpx.AsyncClient() as client:
            search_response = await client.post(
                f"{VECTOR_DB_SERVICE}/qdrant/collections/{collection_name}/search",
                json={
                    "query_vector": query_vector,
                    "limit": top_k,
                    "with_payload": True,
                },
            )
            search_response.raise_for_status()
            search_results = search_response.json()
        
        # 2. 构建上下文
        context = "\n".join([
            f"文档 {idx + 1}: {result.get('payload', {}).get('content', '')}"
            for idx, result in enumerate(search_results)
        ])
        
        # 3. 调用 LLM 生成回答
        messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，根据提供的上下文信息回答问题。如果没有相关信息，请明确说明。",
            },
            {
                "role": "user",
                "content": f"基于以下上下文回答问题：\n\n上下文：\n{context}\n\n问题：{query}",
            },
        ]
        
        async with httpx.AsyncClient() as client:
            chat_response = await client.post(
                f"{LLM_SERVICE}/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            chat_response.raise_for_status()
            chat_data = chat_response.json()
        
        answer = chat_data["data"]["choices"][0]["message"]["content"]
        
        return ServiceResponse(
            success=True,
            data={
                "query": query,
                "answer": answer,
                "sources": [
                    {
                        "id": result.get("id"),
                        "content": result.get("payload", {}).get("content", ""),
                        "similarity": result.get("score", 0),
                    }
                    for result in search_results
                ],
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        return ServiceResponse(
            success=False,
            error=f"RAG search failed: {str(e)}",
            version="1.0.0",
            timestamp=time.time(),
        )
