from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import User, TokenData
from .auth_service import auth_service


security = HTTPBearer()


async def get_token_from_request(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """从请求中获取令牌"""
    # 优先从 Authorization header 获取
    if credentials and credentials.scheme == "Bearer":
        return credentials.credentials
    
    # 尝试从 cookie 获取
    token = request.cookies.get("access_token")
    if token:
        return token
    
    return None


async def get_token_data(
    token: Optional[str] = Depends(get_token_from_request),
) -> TokenData:
    """获取令牌数据"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = auth_service.decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


async def get_current_user(
    token_data: TokenData = Depends(get_token_data),
) -> User:
    """获取当前用户"""
    user = auth_service.get_user(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """获取当前超级管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限",
        )
    
    return current_user


def require_permission(permission_id: str):
    """权限验证依赖工厂"""
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_permission(permission_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限: {permission_id}",
            )
        return current_user
    
    return permission_checker


def require_resource_permission(resource: str, action: str):
    """资源权限验证依赖工厂"""
    async def resource_permission_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_resource_permission(resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限: {resource}:{action}",
            )
        return current_user
    
    return resource_permission_checker


def require_role(role_name: str):
    """角色验证依赖工厂"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not current_user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要角色: {role_name}",
            )
        return current_user
    
    return role_checker


class PermissionChecker:
    """权限检查器 - 用于路由权限验证"""
    
    def __init__(self):
        self._auth_service = auth_service
    
    def check(self, user_id: str, permission_id: str) -> bool:
        """检查权限"""
        return self._auth_service.check_permission(user_id, permission_id)
    
    def check_resource(self, user_id: str, resource: str, action: str) -> bool:
        """检查资源权限"""
        return self._auth_service.check_resource_permission(user_id, resource, action)


permission_checker = PermissionChecker()
