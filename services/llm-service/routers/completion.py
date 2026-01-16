from fastapi import APIRouter, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import time

from common import ServiceResponse, LLMException
from services import completion_service


router = APIRouter()


class CompletionRequest(BaseModel):
    model: str = "gpt-3.5-turbo-instruct"
    prompt: str
    suffix: Optional[str] = None
    max_tokens: int = 16
    temperature: float = 1.0
    top_p: float = 1.0
    n: int = 1
    stream: bool = False
    logprobs: Optional[int] = None
    echo: bool = False
    stop: Optional[List[str]] = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    best_of: int = 1
    user: Optional[str] = None


@router.post("/create", tags=["Completion"], summary="创建文本补全")
async def create_completion(request: CompletionRequest):
    try:
        result = completion_service.create_completion(
            model=request.model,
            prompt=request.prompt,
            suffix=request.suffix,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            n=request.n,
            stream=request.stream,
            logprobs=request.logprobs,
            echo=request.echo,
            stop=request.stop,
            presence_penalty=request.presence_penalty,
            frequency_penalty=request.frequency_penalty,
            best_of=request.best_of,
            user=request.user,
        )
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Create completion failed: {str(e)}",
            error_code="COMPLETION_CREATE_FAILED",
        )


@router.post("/batch-create", tags=["Completion"], summary="批量创建文本补全")
async def batch_create_completion(
    prompts: List[str] = Body(...),
    model: str = Body("gpt-3.5-turbo-instruct"),
    max_tokens: int = Body(16),
    temperature: float = Body(1.0),
    batch_size: int = Body(10, ge=1, le=100),
):
    try:
        all_results = []
        for batch in [prompts[i:i+batch_size] for i in range(0, len(prompts), batch_size)]:
            for prompt in batch:
                result = completion_service.create_completion(
                    model=model,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                all_results.append(result)
        
        return ServiceResponse(
            success=True,
            data={
                "results": all_results,
                "total_count": len(all_results),
            },
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Batch create completion failed: {str(e)}",
            error_code="COMPLETION_BATCH_CREATE_FAILED",
        )


@router.get("/models", tags=["Completion"], summary="获取支持的补全模型")
async def get_completion_models():
    try:
        result = completion_service.get_available_models()
        return ServiceResponse(
            success=True,
            data=result,
            version="1.0.0",
            timestamp=time.time(),
        )
    except Exception as e:
        raise LLMException(
            detail=f"Get completion models failed: {str(e)}",
            error_code="COMPLETION_GET_MODELS_FAILED",
        )
