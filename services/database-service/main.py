from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Any
import time

from common import get_settings, ServiceResponse, DatabaseException
from routers import mysql, postgres, mongodb, redis


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    print("\n" + "="*60)
    print(f"  Starting Database Service v{settings.service_version}")
    print("="*60)
    yield
    # 关闭时
    print("\n" + "="*60)
    print(f"  Stopping Database Service v{settings.service_version}")
    print("="*60)


app = FastAPI(
    title="Database Service",
    description="数据库操作服务 - 支持 MySQL、PostgreSQL、MongoDB、Redis",
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


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    if settings.debug:
        print(f"[{time.ctime()}] {request.method} {request.url} - {response.status_code} ({process_time:.4f}s)")
    
    return response


# 全局异常处理
@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
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


# 注册路由
app.include_router(
    mysql.router,
    prefix="/mysql",
    tags=["MySQL"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    postgres.router,
    prefix="/postgres",
    tags=["PostgreSQL"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    mongodb.router,
    prefix="/mongodb",
    tags=["MongoDB"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    redis.router,
    prefix="/redis",
    tags=["Redis"],
    responses={404: {"description": "Not found"}},
)


# 健康检查
@app.get("/health", tags=["Health"], summary="健康检查")
async def health_check() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={"status": "healthy"},
        version=settings.service_version,
        timestamp=time.time(),
    )


# 服务信息
@app.get("/info", tags=["Info"], summary="服务信息")
async def get_service_info() -> ServiceResponse:
    return ServiceResponse(
        success=True,
        data={
            "name": "Database Service",
            "version": settings.service_version,
            "description": "数据库操作服务",
            "supported_databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
            "endpoints": [
                "/mysql",
                "/postgres",
                "/mongodb",
                "/redis",
            ],
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
