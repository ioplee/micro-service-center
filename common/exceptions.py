from fastapi import HTTPException, status
from typing import Optional


class ServiceException(HTTPException):
    """服务异常基类"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Service error",
        service_name: Optional[str] = None,
        version: Optional[str] = None,
    ):
        self.service_name = service_name
        self.version = version
        super().__init__(status_code=status_code, detail=detail)


class DatabaseException(ServiceException):
    """数据库异常"""
    
    def __init__(
        self,
        detail: str = "Database error",
        service_name: str = "database-service",
        version: str = "1.0.0",
        error_code: Optional[str] = None,
    ):
        self.error_code = error_code
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            service_name=service_name,
            version=version,
        )


class VectorDBException(ServiceException):
    """向量数据库异常"""
    
    def __init__(
        self,
        detail: str = "Vector database error",
        service_name: str = "vector-db-service",
        version: str = "1.0.0",
        error_code: Optional[str] = None,
    ):
        self.error_code = error_code
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            service_name=service_name,
            version=version,
        )


class LLMException(ServiceException):
    """LLM服务异常"""
    
    def __init__(
        self,
        detail: str = "LLM service error",
        service_name: str = "llm-service",
        version: str = "1.0.0",
        error_code: Optional[str] = None,
    ):
        self.error_code = error_code
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            service_name=service_name,
            version=version,
        )


class ServiceNotFoundException(ServiceException):
    """服务未找到异常"""
    
    def __init__(
        self,
        service_name: str,
        version: Optional[str] = None,
    ):
        detail = f"Service '{service_name}' not found"
        if version:
            detail += f" with version '{version}'"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            service_name=service_name,
            version=version,
        )


class VersionNotFoundException(ServiceException):
    """版本未找到异常"""
    
    def __init__(
        self,
        service_name: str,
        version: str,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version '{version}' not found for service '{service_name}'",
            service_name=service_name,
            version=version,
        )


class ValidationException(ServiceException):
    """参数验证异常"""
    
    def __init__(
        self,
        detail: str = "Validation error",
        field: Optional[str] = None,
    ):
        if field:
            detail = f"Field '{field}': {detail}"
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class AuthenticationException(ServiceException):
    """认证异常"""
    
    def __init__(
        self,
        detail: str = "Authentication required",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationException(ServiceException):
    """授权异常"""
    
    def __init__(
        self,
        detail: str = "Not authorized",
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )
