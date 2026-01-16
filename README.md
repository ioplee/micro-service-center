# Micro Service Center

基于 FastAPI 的微服务体系，具备版本管理、分层分级 API 结构的能力中台设计。

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
│              (统一入口、版本管理、路由转发)                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────┼──────────────────────────────────────────┐
│              Business Services                               │
│  (业务层按需组合基础能力服务)                                  │
└──────────────────┼──────────────────────────────────────────┘
                   │
┌──────────────────┼──────────────────────────────────────────┐
│              Capability Services                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │  Database   │ │ Vector DB   │ │    LLM      │            │
│  │  Service    │ │  Service    │ │  Service    │            │
│  │ (MySQL/PG/  │ │ (Qdrant/    │ │ (Embedding/ │            │
│  │  MongoDB/   │ │  Milvus/    │ │  LLM Call)  │            │
│  │  Redis)     │ │  ChromaDB)  │ │             │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 项目结构

```
micro-service-center/
├── api-gateway/              # API 网关（统一入口）
│   ├── main.py
│   ├── routes/
│   └── version_manager.py
├── services/                 # 能力服务层
│   ├── database-service/     # 数据库操作服务
│   ├── vector-db-service/    # 向量数据库服务
│   └── llm-service/          # LLM 能力服务
├── business/                 # 业务服务层
│   └── example-service/      # 示例业务服务
├── common/                   # 公共模块
│   ├── base_service.py
│   ├── versioning.py
│   └── exceptions.py
├── docker-compose.yml
└── requirements.txt
```

## 核心特性

- ✅ **版本管理**: 支持服务版本和 API 版本管理
- ✅ **分层架构**: 能力层与业务层分离
- ✅ **多数据库支持**: MySQL、PostgreSQL、MongoDB、Redis
- ✅ **向量数据库支持**: Qdrant、Milvus、ChromaDB
- ✅ **LLM 集成**: Embedding 能力、LLM 调用
- ✅ **统一 API 网关**: 统一入口、路由转发、负载均衡

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 API 网关
cd api-gateway
uvicorn main:app --reload --port 8000

# 启动能力服务
cd services/database-service
uvicorn main:app --reload --port 8001

cd services/vector-db-service
uvicorn main:app --reload --port 8002

cd services/llm-service
uvicorn main:app --reload --port 8003

# 启动业务服务
cd business/example-service
uvicorn main:app --reload --port 8010
```

## docker 启动：
```bash
docker-compose up -d
```

## API 版本管理

```
# v1 版本 API
http://localhost:8000/v1/business/example/...

# v2 版本 API
http://localhost:8000/v2/business/example/...
```

## 版块相应说明
### 已完成的核心功能
### 1. API 网关 (api-gateway/main.py)
- 统一 API 入口
- 版本管理（v1、v2）
- 路由转发到后端服务
- 服务健康检查
### 2. 数据库操作微服务 (database-service)
- MySQL : 完整的 CRUD 操作、批量操作
- PostgreSQL : 完整的 CRUD 操作、批量操作
- MongoDB : 文档操作、聚合查询
- Redis : 字符串、哈希、列表、集合、有序集合操作
### 3. 向量数据库微服务 (vector-db-service)
- Qdrant : 集合管理、向量搜索、滚动查询
- Milvus : 集合管理、向量搜索、索引管理
- ChromaDB : 文档管理、语义搜索
### 4. LLM 能力微服务 (llm-service)
- Embedding : OpenAI 嵌入、本地模型支持
- Completion : 文本补全
- Chat : 聊天补全、流式响应
### 5. 业务层示例服务 (example-service)
- 语义搜索 : 组合 LLM + 向量数据库
- 混合搜索 : 语义 + 关键词搜索
- RAG 搜索 : 检索增强生成
- 聊天服务 : 带历史记录的聊天
### 6. 公共模块 (common)
- 版本管理 : SemVer 规范支持
- 异常处理 : 统一的异常体系
- 配置管理 : 环境变量支持
- 基础服务 : 服务注册、响应模型

## 服务间通信

使用 HTTP/REST 或 gRPC 进行服务间通信，通过服务发现机制实现动态路由。

## License

MIT
