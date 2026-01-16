from fastapi import APIRouter, Request, HTTPException, status
from typing import Any
import httpx
import time

from common import ServiceResponse


router = APIRouter(
    prefix="/v2",
    tags=["v2"],
)


# v2 服务路由配置
V2_SERVICE_ROUTES = {
    "database": "http://localhost:8001",
    "vector-db": "http://localhost:8002",
    "llm": "http://localhost:8003",
    "example": "http://localhost:8010",
}


async def proxy_request(
    request: Request,
    service_name: str,
    path: str,
) -> Any:
    """代理请求到后端服务"""
    if service_name not in V2_SERVICE_ROUTES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found",
        )
    
    base_url = V2_SERVICE_ROUTES[service_name]
    target_url = f"{base_url}{path}"
    
    try:
        # 构建请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
                content=await request.body(),
                params=request.query_params,
            )
        
        return response
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service '{service_name}' unavailable: {str(e)}",
        )


# Database Service
@router.api_route("/database/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_database(request: Request, path: str):
    response = await proxy_request(request, "database", f"/{path}")
    return ServiceResponse(
        success=True,
        data=response.json(),
        version="2.0.0",
        timestamp=time.time(),
    )


# Vector Database Service
@router.api_route("/vector-db/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_vector_db(request: Request, path: str):
    response = await proxy_request(request, "vector-db", f"/{path}")
    return ServiceResponse(
        success=True,
        data=response.json(),
        version="2.0.0",
        timestamp=time.time(),
    )


# LLM Service
@router.api_route("/llm/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_llm(request: Request, path: str):
    response = await proxy_request(request, "llm", f"/{path}")
    return ServiceResponse(
        success=True,
        data=response.json(),
        version="2.0.0",
        timestamp=time.time(),
    )


# Example Business Service
@router.api_route("/business/example/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_example(request: Request, path: str):
    response = await proxy_request(request, "example", f"/{path}")
    return ServiceResponse(
        success=True,
        data=response.json(),
        version="2.0.0",
        timestamp=time.time(),
    )


# v2 版本信息
@router.get("/info", tags=["v2"], summary="v2 版本信息")
async def get_v2_info() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={
            "version": "2.0.0",
            "name": "API v2",
            "description": "v2 版本 API - 支持更多特性",
            "services": list(V2_SERVICE_ROUTES.keys()),
            "improvements": [
                "增强的错误处理",
                "更好的性能优化",
                "新增服务支持",
                "改进的 API 设计",
            ],
        },
        version="2.0.0",
        timestamp=time.time(),
    )
