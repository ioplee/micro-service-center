from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Any
import time

from common import get_settings, ServiceResponse, LLMException
from routers import embedding, completion, chat


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print(f"  Starting LLM Service v{settings.service_version}")
    print("="*60)
    yield
    print("\n" + "="*60)
    print(f"  Stopping LLM Service v{settings.service_version}")
    print("="*60)


app = FastAPI(
    title="LLM Service",
    description="LLM 能力服务 - 支持 Embedding、Completion、Chat",
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


@app.exception_handler(LLMException)
async def llm_exception_handler(request: Request, exc: LLMException):
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
    embedding.router,
    prefix="/embedding",
    tags=["Embedding"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    completion.router,
    prefix="/completion",
    tags=["Completion"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"],
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
            "name": "LLM Service",
            "version": settings.service_version,
            "description": "LLM 能力服务",
            "supported_models": {
                "embedding": ["text-embedding-3-small", "text-embedding-3-large"],
                "completion": ["gpt-3.5-turbo-instruct", "gpt-4"],
                "chat": ["gpt-3.5-turbo", "gpt-4"],
            },
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
