from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    version: str
    timestamp: float


class BaseService(ABC):
    """基础服务抽象类"""
    
    service_name: str
    service_version: str
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.service_name = name
        self.service_version = version
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        pass
    
    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """获取服务信息"""
        pass


class ServiceRegistry:
    """服务注册中心"""
    
    _services: Dict[str, BaseService] = {}
    _service_endpoints: Dict[str, str] = {}
    
    @classmethod
    def register(cls, service: BaseService, endpoint: str):
        key = f"{service.service_name}:{service.service_version}"
        cls._services[key] = service
        cls._service_endpoints[key] = endpoint
    
    @classmethod
    def get_service(cls, name: str, version: str = "1.0.0") -> Optional[BaseService]:
        key = f"{name}:{version}"
        return cls._services.get(key)
    
    @classmethod
    def get_service_endpoint(cls, name: str, version: str = "1.0.0") -> Optional[str]:
        key = f"{name}:{version}"
        return cls._service_endpoints.get(key)
    
    @classmethod
    def list_services(cls) -> Dict[str, Any]:
        return {
            "services": list(cls._services.keys()),
            "endpoints": cls._service_endpoints
        }
