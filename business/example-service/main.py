from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Any
import time
import httpx

from common import get_settings, ServiceResponse
from routers import search, chat, data


settings = get_settings()


# 基础服务配置
BASE_SERVICES = {
    "database": "http://localhost:8001",
    "vector-db": "http://localhost:8002",
    "llm": "http://localhost:8003",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print(f"  Starting Example Business Service v{settings.service_version}")
    print("="*60)
    yield
    print("\n" + "="*60)
    print(f"  Stopping Example Business Service v{settings.service_version}")
    print("="*60)


app = FastAPI(
    title="Example Business Service",
    description="示例业务服务 - 组合基础能力服务",
    version=settings.service_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    if settings.debug:
        print(f"[{time.ctime()}] {request.method} {request.url} - {response.status_code} ({process_time:.4f}s)")
    
    return response


app.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    data.router,
    prefix="/data",
    tags=["Data"],
    responses={404: {"description": "Not found"}},
)


@app.get("/health", tags=["Health"], summary="健康检查")
async def health_check() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={"status": "healthy"},
        version=settings.service_version,
        timestamp=time.time(),
    )


@app.get("/info", tags=["Info"], summary="服务信息")
async def get_service_info() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={
            "name": "Example Business Service",
            "version": settings.service_version,
            "description": "示例业务服务",
            "base_services": BASE_SERVICES,
        },
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
