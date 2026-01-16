from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    # 基础配置
    project_name: str = "Micro Service Center"
    project_version: str = "1.0.0"
    debug: bool = False
    
    # API 配置
    api_prefix: str = "/api"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # 服务配置
    service_name: str = "base-service"
    service_version: str = "1.0.0"
    service_port: int = 8000
    
    # 数据库配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "app"
    
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = ""
    postgres_db: str = "app"
    
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_db: str = "app"
    mongodb_user: Optional[str] = None
    mongodb_password: Optional[str] = None
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # 向量数据库配置
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: Optional[str] = None
    
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_user: Optional[str] = None
    milvus_password: Optional[str] = None
    
    chromadb_path: str = "./chroma_data"
    
    # LLM 配置
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-3.5-turbo"
    
    # 服务注册
    service_registry_url: Optional[str] = None
    
    # CORS 配置
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
