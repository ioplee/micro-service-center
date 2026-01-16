# 变更记录

所有重要的项目变更都将记录在此文件中。

## [1.0.0] - 2026-01-16

### ✨ 新增功能

#### 1. 微服务架构基础框架
- ✅ 基于 FastAPI 的微服务架构
- ✅ 分层分级 API 结构
- ✅ 版本管理系统（v1、v2）
- ✅ 统一 API 网关

#### 2. 数据库操作微服务
- ✅ MySQL 支持（完整 CRUD、批量操作）
- ✅ PostgreSQL 支持（完整 CRUD、批量操作）
- ✅ MongoDB 支持（文档操作、聚合查询）
- ✅ Redis 支持（字符串、哈希、列表、集合、有序集合）

#### 3. 向量数据库微服务
- ✅ Qdrant 支持（集合管理、向量搜索、滚动查询）
- ✅ Milvus 支持（集合管理、向量搜索、索引管理）
- ✅ ChromaDB 支持（文档管理、语义搜索）

#### 4. LLM 能力微服务
- ✅ vLLM 集成（高性能推理引擎）
- ✅ Ollama Embedding 服务（中文嵌入）
- ✅ 聊天补全（Chat Completion）
- ✅ 文本补全（Text Completion）
- ✅ 流式响应支持

#### 5. 业务层示例服务
- ✅ 语义搜索
- ✅ 混合搜索（语义 + 关键词）
- ✅ RAG 搜索（检索增强生成）
- ✅ 带历史记录的聊天服务
- ✅ 文档管理

#### 6. 用户权限管理模块
- ✅ 用户认证（JWT Token）
- ✅ 用户管理（注册、登录、信息管理）
- ✅ 角色管理（创建、分配、删除）
- ✅ 权限管理（资源 + 操作）
- ✅ 依赖注入装饰器
- ✅ 12 个系统默认权限
- ✅ 3 个系统默认角色（admin、user、developer）

#### 7. 公共模块
- ✅ 基础服务类
- ✅ 版本管理工具
- ✅ 异常处理体系
- ✅ 配置管理（环境变量支持）
- ✅ 服务注册

#### 8. 部署支持
- ✅ Docker Compose 配置
- ✅ 环境变量示例文件
- ✅ 完整的依赖清单

### 🔧 技术栈

- **框架**: FastAPI 0.109.0
- **认证**: JWT、bcrypt
- **数据库**: MySQL、PostgreSQL、MongoDB、Redis
- **向量数据库**: Qdrant、Milvus、ChromaDB
- **LLM**: vLLM 0.4.0、Ollama
- **部署**: Docker、Docker Compose

### 📁 项目结构

```
micro-service-center/
├── api-gateway/              # API 网关
│   ├── routes/
│   │   ├── v1.py
│   │   ├── v2.py
│   │   └── auth/            # 认证路由
│   └── main.py
├── services/                 # 能力服务层
│   ├── database-service/     # 数据库操作服务
│   ├── vector-db-service/    # 向量数据库服务
│   └── llm-service/          # LLM 能力服务
├── business/                 # 业务服务层
│   └── example-service/      # 示例业务服务
├── common/                   # 公共模块
│   ├── auth/                 # 权限管理模块
│   ├── base_service.py
│   ├── config.py
│   ├── exceptions.py
│   └── versioning.py
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### 🚀 快速开始

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 启动 Ollama
```bash
ollama serve
ollama pull shaw/dmeta-embedding-zh
```

#### 3. 启动 vLLM
```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen-7B-Chat \
    --host 0.0.0.0 \
    --port 8000
```

#### 4. 启动微服务
```bash
# API 网关
cd api-gateway
uvicorn main:app --reload --port 8000

# 数据库服务
cd services/database-service
uvicorn main:app --reload --port 8001

# 向量数据库服务
cd services/vector-db-service
uvicorn main:app --reload --port 8002

# LLM 服务
cd services/llm-service
uvicorn main:app --reload --port 8003

# 示例业务服务
cd business/example-service
uvicorn main:app --reload --port 8010
```

#### 5. Docker 部署
```bash
docker-compose up -d
```

### 📡 API 端点

#### 认证端点
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册
- `POST /auth/logout` - 用户登出
- `GET /auth/users/me` - 获取当前用户信息

#### 用户管理
- `GET /auth/users` - 获取用户列表
- `GET /auth/users/{user_id}` - 获取用户信息
- `PUT /auth/users/{user_id}` - 更新用户信息
- `DELETE /auth/users/{user_id}` - 删除用户

#### 角色管理
- `GET /auth/roles` - 获取角色列表
- `GET /auth/roles/{role_id}` - 获取角色信息
- `POST /auth/roles` - 创建角色
- `PUT /auth/roles/{role_id}` - 更新角色
- `DELETE /auth/roles/{role_id}` - 删除角色

#### 权限管理
- `GET /auth/permissions` - 获取权限列表
- `GET /auth/check-permission/{permission_id}` - 检查权限

#### v1 API
- `GET /v1/health` - 健康检查
- `GET /v1/info` - 版本信息
- `POST /v1/llm/chat/completions` - 聊天补全
- `POST /v1/llm/embedding/create` - 创建嵌入向量
- `POST /v1/business/example/search/semantic` - 语义搜索

### 🔐 默认账户

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: 超级管理员

### 📝 配置说明

#### vLLM 配置
```bash
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL=Qwen/Qwen-7B-Chat
```

#### Ollama 配置
```bash
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_EMBEDDING_MODEL=shaw/dmeta-embedding-zh
```

### 🎯 设计特点

1. **分层架构**: 能力层与业务层分离
2. **版本管理**: 支持 API 版本迭代
3. **松耦合**: 服务间通过 HTTP/REST 通信
4. **可扩展**: 易于添加新服务
5. **安全**: JWT 认证 + 权限验证
6. **容器化**: 完整的 Docker 支持

### 📄 许可证

MIT License

---

*此变更记录文件将持续更新，记录项目的所有重要变更。*
