from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import Optional, List
from pydantic import BaseModel, EmailStr
import time

from common.auth import (
    auth_service,
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    require_permission,
    require_role,
    User,
    Role,
    Permission,
    UserStatus,
    LoginRequest,
    RegisterRequest,
    UserUpdateRequest,
    RoleUpdateRequest,
    PermissionUpdateRequest,
)


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={401: {"description": "未认证"}},
)


# ========== 认证端点 ==========

@router.post("/login", summary="用户登录")
async def login(request: LoginRequest, response: Response):
    """用户登录并获取访问令牌"""
    token = auth_service.authenticate(request.username, request.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 设置 cookie
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        max_age=3600 * 24 * 7,
        samesite="lax",
    )
    
    return {
        "access_token": token.access_token,
        "token_type": token.token_type,
        "expires_at": token.expires_at,
    }


@router.post("/register", summary="用户注册")
async def register(request: RegisterRequest):
    """注册新用户"""
    try:
        user = auth_service.register(
            username=request.username,
            password=request.password,
            email=request.email,
            full_name=request.full_name,
        )
        
        return {
            "success": True,
            "message": "注册成功",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "status": user.status.value,
            },
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/logout", summary="用户登出")
async def logout(response: Response):
    """用户登出"""
    response.delete_cookie(key="access_token")
    return {"success": True, "message": "登出成功"}


# ========== 用户端点 ==========

@router.get("/users/me", summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """获取当前登录用户的信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "status": current_user.status.value,
        "is_superuser": current_user.is_superuser,
        "roles": [
            {"id": r.id, "name": r.name} for r in current_user.roles
        ],
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
    }


@router.get("/users", summary="获取用户列表", dependencies=[Depends(require_role("admin"))])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
):
    """获取用户列表（需要管理员权限）"""
    users = auth_service.list_users(skip=skip, limit=limit)
    
    return {
        "total": len(users),
        "skip": skip,
        "limit": limit,
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "status": u.status.value,
                "is_superuser": u.is_superuser,
                "roles": [{"id": r.id, "name": r.name} for r in u.roles],
                "last_login": u.last_login,
                "created_at": u.created_at,
            }
            for u in users
        ],
    }


@router.get("/users/{user_id}", summary="获取用户信息", dependencies=[Depends(require_permission("user:read"))])
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """获取指定用户的信息"""
    user = auth_service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "status": user.status.value,
        "is_superuser": user.is_superuser,
        "roles": [{"id": r.id, "name": r.name} for r in user.roles],
        "last_login": user.last_login,
        "created_at": user.created_at,
    }


@router.put("/users/{user_id}", summary="更新用户信息", dependencies=[Depends(require_permission("user:write"))])
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """更新用户信息"""
    # 普通用户只能更新自己的信息
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能更新自己的信息",
        )
    
    update_data = {}
    if request.email is not None:
        update_data["email"] = request.email
    if request.full_name is not None:
        update_data["full_name"] = request.full_name
    if request.status is not None and current_user.is_superuser:
        update_data["status"] = request.status
    if request.roles is not None and current_user.is_superuser:
        update_data["roles"] = request.roles
    
    user = auth_service.update_user(user_id, **update_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return {"success": True, "message": "用户信息已更新"}


@router.delete("/users/{user_id}", summary="删除用户", dependencies=[Depends(require_permission("user:delete"))])
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
):
    """删除用户（需要超级管理员权限）"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己",
        )
    
    success = auth_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    return {"success": True, "message": "用户已删除"}


# ========== 角色端点 ==========

@router.get("/roles", summary="获取角色列表")
async def list_roles(current_user: User = Depends(get_current_active_user)):
    """获取所有角色列表"""
    roles = auth_service.list_roles()
    
    return {
        "total": len(roles),
        "roles": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "is_default": r.is_default,
                "is_system": r.is_system,
                "permission_count": len(r.permissions),
                "created_at": r.created_at,
            }
            for r in roles
        ],
    }


@router.get("/roles/{role_id}", summary="获取角色信息", dependencies=[Depends(require_permission("role:read"))])
async def get_role(
    role_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """获取指定角色的信息"""
    role = auth_service.get_role(role_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="角色不存在",
        )
    
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "is_default": role.is_default,
        "is_system": role.is_system,
        "permissions": [
            {"id": p.id, "name": p.name, "resource": p.resource, "action": p.action}
            for p in role.permissions
        ],
        "created_at": role.created_at,
        "updated_at": role.updated_at,
    }


@router.post("/roles", summary="创建角色", dependencies=[Depends(require_role("admin"))])
async def create_role(
    name: str,
    description: Optional[str] = None,
    permissions: Optional[List[str]] = None,
    is_default: bool = False,
    current_user: User = Depends(get_current_superuser),
):
    """创建新角色（需要超级管理员权限）"""
    try:
        role = auth_service.create_role(
            name=name,
            description=description,
            permissions=permissions,
            is_default=is_default,
        )
        
        return {
            "success": True,
            "message": "角色已创建",
            "role": {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_default": role.is_default,
            },
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/roles/{role_id}", summary="更新角色", dependencies=[Depends(require_permission("role:write"))])
async def update_role(
    role_id: str,
    request: RoleUpdateRequest,
    current_user: User = Depends(get_current_superuser),
):
    """更新角色信息（需要超级管理员权限）"""
    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.description is not None:
        update_data["description"] = request.description
    if request.permissions is not None:
        update_data["permissions"] = request.permissions
    
    try:
        role = auth_service.update_role(role_id, **update_data)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )
        
        return {"success": True, "message": "角色信息已更新"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/roles/{role_id}", summary="删除角色", dependencies=[Depends(require_permission("role:write"))])
async def delete_role(
    role_id: str,
    current_user: User = Depends(get_current_superuser),
):
    """删除角色（需要超级管理员权限）"""
    try:
        success = auth_service.delete_role(role_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在",
            )
        
        return {"success": True, "message": "角色已删除"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ========== 权限端点 ==========

@router.get("/permissions", summary="获取权限列表")
async def list_permissions(current_user: User = Depends(get_current_active_user)):
    """获取所有权限列表"""
    permissions = auth_service.list_permissions()
    
    return {
        "total": len(permissions),
        "permissions": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "resource": p.resource,
                "action": p.action,
                "created_at": p.created_at,
            }
            for p in permissions
        ],
    }


@router.get("/permissions/{permission_id}", summary="获取权限信息")
async def get_permission(
    permission_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """获取指定权限的信息"""
    permission = auth_service.get_permission(permission_id)
    
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在",
        )
    
    return {
        "id": permission.id,
        "name": permission.name,
        "description": permission.description,
        "resource": permission.resource,
        "action": permission.action,
        "created_at": permission.created_at,
    }


# ========== 权限检查端点 ==========

@router.get("/check-permission/{permission_id}", summary="检查权限")
async def check_permission(
    permission_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """检查当前用户是否拥有指定权限"""
    has_perm = current_user.has_permission(permission_id)
    
    return {
        "permission_id": permission_id,
        "has_permission": has_perm,
    }


@router.get("/check-resource-permission/{resource}/{action}", summary="检查资源权限")
async def check_resource_permission(
    resource: str,
    action: str,
    current_user: User = Depends(get_current_active_user),
):
    """检查当前用户是否拥有指定资源的操作权限"""
    has_perm = current_user.has_resource_permission(resource, action)
    
    return {
        "resource": resource,
        "action": action,
        "has_permission": has_perm,
    }
