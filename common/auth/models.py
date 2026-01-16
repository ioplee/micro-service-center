from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
import time
from datetime import datetime


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Permission(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Permission):
            return self.id == other.id
        return False


class Role(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)
    is_default: bool = False
    is_system: bool = False
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def has_permission(self, permission_id: str) -> bool:
        return any(p.id == permission_id for p in self.permissions)

    def has_resource_permission(self, resource: str, action: str) -> bool:
        return any(
            p.resource == resource and p.action == action
            for p in self.permissions
        )

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
            self.updated_at = time.time()

    def remove_permission(self, permission_id: str):
        self.permissions = [
            p for p in self.permissions if p.id != permission_id
        ]
        self.updated_at = time.time()


class User(BaseModel):
    id: str
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    hashed_password: str
    roles: List[Role] = Field(default_factory=list)
    status: UserStatus = UserStatus.ACTIVE
    is_superuser: bool = False
    last_login: Optional[float] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_id: str) -> bool:
        if self.is_superuser:
            return True
        return any(role.has_permission(permission_id) for role in self.roles)

    def has_resource_permission(self, resource: str, action: str) -> bool:
        if self.is_superuser:
            return True
        return any(
            role.has_resource_permission(resource, action)
            for role in self.roles
        )

    def add_role(self, role: Role):
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = time.time()

    def remove_role(self, role_id: str):
        self.roles = [r for r in self.roles if r.id != role_id]
        self.updated_at = time.time()

    def update_last_login(self):
        self.last_login = time.time()


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: float


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None
    roles: Optional[List[str]] = None


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class PermissionUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


# 系统默认权限
DEFAULT_PERMISSIONS = [
    Permission(
        id="user:read",
        name="读取用户信息",
        description="允许读取用户信息",
        resource="user",
        action="read",
    ),
    Permission(
        id="user:write",
        name="修改用户信息",
        description="允许修改用户信息",
        resource="user",
        action="write",
    ),
    Permission(
        id="user:delete",
        name="删除用户",
        description="允许删除用户",
        resource="user",
        action="delete",
    ),
    Permission(
        id="role:read",
        name="读取角色信息",
        description="允许读取角色信息",
        resource="role",
        action="read",
    ),
    Permission(
        id="role:write",
        name="修改角色信息",
        description="允许修改角色信息",
        resource="role",
        action="write",
    ),
    Permission(
        id="permission:read",
        name="读取权限信息",
        description="允许读取权限信息",
        resource="permission",
        action="read",
    ),
    Permission(
        id="llm:chat",
        name="使用LLM聊天功能",
        description="允许调用LLM聊天接口",
        resource="llm",
        action="chat",
    ),
    Permission(
        id="llm:embedding",
        name="使用LLM嵌入功能",
        description="允许调用LLM嵌入接口",
        resource="llm",
        action="embedding",
    ),
    Permission(
        id="database:read",
        name="读取数据库",
        description="允许读取数据库数据",
        resource="database",
        action="read",
    ),
    Permission(
        id="database:write",
        name="写入数据库",
        description="允许写入数据库数据",
        resource="database",
        action="write",
    ),
    Permission(
        id="vector_db:search",
        name="向量数据库搜索",
        description="允许在向量数据库中搜索",
        resource="vector_db",
        action="search",
    ),
    Permission(
        id="vector_db:write",
        name="向量数据库写入",
        description="允许向向量数据库写入数据",
        resource="vector_db",
        action="write",
    ),
]


# 系统默认角色
DEFAULT_ROLES = [
    Role(
        id="admin",
        name="超级管理员",
        description="拥有所有权限的超级管理员角色",
        permissions=DEFAULT_PERMISSIONS,
        is_default=False,
        is_system=True,
    ),
    Role(
        id="user",
        name="普通用户",
        description="拥有基本权限的普通用户角色",
        permissions=[
            p for p in DEFAULT_PERMISSIONS
            if p.id in ["user:read", "llm:chat", "llm:embedding", "vector_db:search"]
        ],
        is_default=True,
        is_system=True,
    ),
    Role(
        id="developer",
        name="开发者",
        description="拥有开发相关权限的角色",
        permissions=[
            p for p in DEFAULT_PERMISSIONS
            if p.id not in ["user:delete", "role:write"]
        ],
        is_default=False,
        is_system=True,
    ),
]
