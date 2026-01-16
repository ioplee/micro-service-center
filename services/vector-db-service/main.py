from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Any
import time

from common import get_settings, ServiceResponse, VectorDBException
from routers import qdrant, milvus, chromadb


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print(f"  Starting Vector Database Service v{settings.service_version}")
    print("="*60)
    yield
    print("\n" + "="*60)
    print(f"  Stopping Vector Database Service v{settings.service_version}")
    print("="*60)


app = FastAPI(
    title="Vector Database Service",
    description="向量数据库操作服务 - 支持 Qdrant、Milvus、ChromaDB",
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


@app.exception_handler(VectorDBException)
async def vector_db_exception_handler(request: Request, exc: VectorDBException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ServiceResponse(
            success=False,
            error=exc.detail,
            version=settings.service_version,
            timestamp=time.time(),
        ).dict(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ServiceResponse(
            success=False,
            error=f"Internal server error: {str(exc)}",
            version=settings.service_version,
            timestamp=time.time(),
        ).dict(),
    )


app.include_router(
    qdrant.router,
    prefix="/qdrant",
    tags=["Qdrant"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    milvus.router,
    prefix="/milvus",
    tags=["Milvus"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    chromadb.router,
    prefix="/chromadb",
    tags=["ChromaDB"],
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
            "name": "Vector Database Service",
            "version": settings.service_version,
            "description": "向量数据库操作服务",
            "supported_databases": ["Qdrant", "Milvus", "ChromaDB"],
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
