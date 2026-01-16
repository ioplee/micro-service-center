from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import time
import uuid

from common import get_settings
from .models import User, Role, Permission, Token, TokenData, UserStatus, DEFAULT_PERMISSIONS, DEFAULT_ROLES


settings = get_settings()


# JWT 配置
SECRET_KEY = "your-secret-key-here-change-in-production"  # 生产环境应使用环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天


# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """认证服务 - 处理用户认证、授权和权限管理"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._init_default_data()
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 初始化权限
        for perm in DEFAULT_PERMISSIONS:
            self._permissions[perm.id] = perm
        
        # 初始化角色
        for role in DEFAULT_ROLES:
            self._roles[role.id] = role
        
        # 创建默认管理员用户
        admin_user = User(
            id="admin-001",
            username="admin",
            email="admin@example.com",
            full_name="Administrator",
            hashed_password=self.hash_password("admin123"),
            roles=[self._roles["admin"]],
            status=UserStatus.ACTIVE,
            is_superuser=True,
        )
        self._users["admin-001"] = admin_user
        
        print("✓ 认证服务初始化成功")
        print(f"  - 默认权限: {len(self._permissions)} 个")
        print(f"  - 默认角色: {len(self._roles)} 个")
        print(f"  - 默认用户: {len(self._users)} 个")
    
    # ========== 密码操作 ==========
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ========== JWT 操作 ==========
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            roles: List[str] = payload.get("roles", [])
            permissions: List[str] = payload.get("permissions", [])
            
            if user_id is None:
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                roles=roles,
                permissions=permissions,
            )
        except JWTError:
            return None
    
    # ========== 用户操作 ==========
    
    def register(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role_ids: Optional[List[str]] = None,
    ) -> User:
        """注册新用户"""
        # 检查用户名是否已存在
        if any(user.username == username for user in self._users.values()):
            raise ValueError(f"用户名 '{username}' 已存在")
        
        # 确定用户角色
        if role_ids:
            roles = [self._roles[rid] for rid in role_ids if rid in self._roles]
        else:
            # 默认角色
            roles = [r for r in self._roles.values() if r.is_default]
        
        if not roles:
            roles = [self._roles["user"]]
        
        user = User(
            id=f"user-{uuid.uuid4().hex[:8]}",
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=self.hash_password(password),
            roles=roles,
            status=UserStatus.ACTIVE,
            is_superuser=False,
        )
        
        self._users[user.id] = user
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[Token]:
        """用户认证"""
        # 查找用户
        user = next(
            (u for u in self._users.values() if u.username == username),
            None
        )
        
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        # 更新最后登录时间
        user.update_last_login()
        
        # 收集权限
        permissions = []
        for role in user.roles:
            permissions.extend([p.id for p in role.permissions])
        permissions = list(set(permissions))
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "roles": [r.id for r in user.roles],
                "permissions": permissions,
            },
            expires_delta=access_token_expires,
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=time.time() + access_token_expires.total_seconds(),
        )
    
    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取用户"""
        return next(
            (u for u in self._users.values() if u.username == username),
            None
        )
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """更新用户信息"""
        user = self._users.get(user_id)
        if not user:
            return None
        
        if "email" in kwargs:
            user.email = kwargs["email"]
        if "full_name" in kwargs:
            user.full_name = kwargs["full_name"]
        if "status" in kwargs:
            user.status = kwargs["status"]
        if "password" in kwargs:
            user.hashed_password = self.hash_password(kwargs["password"])
        if "roles" in kwargs:
            user.roles = [
                self._roles[rid] for rid in kwargs["roles"] if rid in self._roles
            ]
        
        user.updated_at = time.time()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """列出用户"""
        users = list(self._users.values())
        users.sort(key=lambda u: u.created_at, reverse=True)
        return users[skip:skip + limit]
    
    # ========== 角色操作 ==========
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """获取角色"""
        return self._roles.get(role_id)
    
    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        is_default: bool = False,
    ) -> Role:
        """创建角色"""
        role_id = f"role-{uuid.uuid4().hex[:8]}"
        
        perm_list = []
        if permissions:
            perm_list = [
                self._permissions[p] for p in permissions if p in self._permissions
            ]
        
        role = Role(
            id=role_id,
            name=name,
            description=description,
            permissions=perm_list,
            is_default=is_default,
            is_system=False,
        )
        
        self._roles[role_id] = role
        return role
    
    def update_role(self, role_id: str, **kwargs) -> Optional[Role]:
        """更新角色"""
        role = self._roles.get(role_id)
        if not role:
            return None
        
        if role.is_system:
            raise ValueError("系统角色不允许修改")
        
        if "name" in kwargs:
            role.name = kwargs["name"]
        if "description" in kwargs:
            role.description = kwargs["description"]
        if "permissions" in kwargs:
            role.permissions = [
                self._permissions[p] for p in kwargs["permissions"]
                if p in self._permissions
            ]
        if "is_default" in kwargs:
            role.is_default = kwargs["is_default"]
        
        role.updated_at = time.time()
        return role
    
    def delete_role(self, role_id: str) -> bool:
        """删除角色"""
        role = self._roles.get(role_id)
        if not role:
            return False
        
        if role.is_system:
            raise ValueError("系统角色不允许删除")
        
        # 从用户中移除该角色
        for user in self._users.values():
            user.remove_role(role_id)
        
        del self._roles[role_id]
        return True
    
    def list_roles(self) -> List[Role]:
        """列出角色"""
        return list(self._roles.values())
    
    # ========== 权限操作 ==========
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """获取权限"""
        return self._permissions.get(permission_id)
    
    def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None,
    ) -> Permission:
        """创建权限"""
        permission_id = f"{resource}:{action}"
        
        if permission_id in self._permissions:
            raise ValueError(f"权限 '{permission_id}' 已存在")
        
        permission = Permission(
            id=permission_id,
            name=name,
            description=description,
            resource=resource,
            action=action,
        )
        
        self._permissions[permission_id] = permission
        return permission
    
    def list_permissions(self) -> List[Permission]:
        """列出权限"""
        return list(self._permissions.values())
    
    # ========== 权限检查 ==========
    
    def check_permission(self, user_id: str, permission_id: str) -> bool:
        """检查用户是否拥有指定权限"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        return user.has_permission(permission_id)
    
    def check_resource_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> bool:
        """检查用户是否拥有指定资源的操作权限"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        return user.has_resource_permission(resource, action)


# 全局认证服务实例
auth_service = AuthService()
