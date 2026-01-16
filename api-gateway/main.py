from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from typing import Any, Dict
import time
import httpx

from common import get_settings, ServiceResponse, ServiceNotFoundException
from common.auth import auth_service
from routes import v1, v2
from routes.auth import auth_router


settings = get_settings()


# 服务路由配置
SERVICE_ROUTES = {
    "v1": {
        "database": "http://localhost:8001",
        "vector-db": "http://localhost:8002",
        "llm": "http://localhost:8003",
        "example": "http://localhost:8010",
    },
    "v2": {
        "database": "http://localhost:8001",
        "vector-db": "http://localhost:8002",
        "llm": "http://localhost:8003",
        "example": "http://localhost:8010",
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print(f"  Starting API Gateway v{settings.service_version}")
    print("="*60)
    yield
    print("\n" + "="*60)
    print(f"  Stopping API Gateway v{settings.service_version}")
    print("="*60)


app = FastAPI(
    title="API Gateway",
    description="统一 API 网关 - 版本管理、路由转发、负载均衡",
    version=settings.service_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# 可信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Gateway-Version"] = settings.service_version
    
    if settings.debug:
        print(f"[{time.ctime()}] {request.method} {request.url} - {response.status_code} ({process_time:.4f}s)")
    
    return response


# 注册认证路由
app.include_router(
    auth_router,
    tags=["Auth"],
)

# 注册版本路由
app.include_router(
    v1.router,
    prefix="/v1",
    tags=["v1"],
)

app.include_router(
    v2.router,
    prefix="/v2",
    tags=["v2"],
)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url=settings.docs_url)


@app.get("/health", tags=["Health"], summary="健康检查")
async def health_check() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={"status": "healthy"},
        version=settings.service_version,
        timestamp=time.time(),
    )


@app.get("/info", tags=["Info"], summary="网关信息")
async def get_gateway_info() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={
            "name": "API Gateway",
            "version": settings.service_version,
            "description": "统一 API 网关",
            "supported_versions": list(SERVICE_ROUTES.keys()),
            "services": SERVICE_ROUTES,
        },
        version=settings.service_version,
        timestamp=time.time(),
    )


@app.get("/routes", tags=["Routes"], summary="路由配置")
async def get_routes() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={
            "routes": SERVICE_ROUTES,
        },
        version=settings.service_version,
        timestamp=time.time(),
    )


@app.get("/services/health", tags=["Services"], summary="服务健康检查")
async def check_services_health() -> ServiceResponse:
    results = {}
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for version, services in SERVICE_ROUTES.items():
            results[version] = {}
            
            for service_name, service_url in services.items():
                try:
                    response = await client.get(f"{service_url}/health")
                    if response.status_code == 200:
                        data = response.json()
                        results[version][service_name] = {
                            "status": "healthy",
                            "url": service_url,
                            "version": data.get("version", "unknown"),
                        }
                    else:
                        results[version][service_name] = {
                            "status": "unhealthy",
                            "url": service_url,
                            "error": f"HTTP {response.status_code}",
                        }
                except Exception as e:
                    results[version][service_name] = {
                        "status": "unhealthy",
                        "url": service_url,
                        "error": str(e),
                    }
    
    return ServiceResponse(
        success=True,
        data=results,
        version=settings.service_version,
        timestamp=time.time(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.service_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
