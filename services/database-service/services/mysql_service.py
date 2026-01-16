from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import asyncio

from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from common import get_settings


settings = get_settings()


class MySQLService:
    """MySQL 数据库服务"""
    
    def __init__(self):
        self._engine = None
        self._Session = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            connection_string = (
                f"mysql+asyncmy://{settings.mysql_user}:{settings.mysql_password}@"
                f"{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_db}"
            )
            
            self._engine = create_engine(
                connection_string,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600,
                pool_pre_ping=True,
            )
            self._Session = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
            )
            
            print("✓ MySQL 连接成功")
        except Exception as e:
            print(f"✗ MySQL 连接失败: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            with self._Session() as session:
                result = session.execute(text("SELECT 1 as status"))
                row = result.fetchone()
                return {
                    "status": "healthy",
                    "database": "MySQL",
                    "version": self._engine.dialect.server_version_info,
                    "connection": "ok",
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "MySQL",
                "error": str(e),
            }
    
    def get_tables(self) -> List[str]:
        """获取所有表"""
        metadata = MetaData()
        metadata.reflect(bind=self._engine)
        return list(metadata.tables.keys())
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """获取表结构"""
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=self._engine)
        
        schema = {
            "table_name": table_name,
            "columns": [],
            "primary_key": [],
        }
        
        for column in table.columns:
            col_info = {
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable,
                "default": column.default,
                "autoincrement": column.autoincrement,
            }
            schema["columns"].append(col_info)
            
            if column.primary_key:
                schema["primary_key"].append(column.name)
        
        return schema
    
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行查询"""
        try:
            with self._Session() as session:
                result = session.execute(text(sql), params or {})
                columns = result.keys()
                rows = result.fetchall()
                
                return {
                    "columns": list(columns),
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "count": len(rows),
                }
        except SQLAlchemyError as e:
            raise Exception(f"SQL 执行错误: {str(e)}")
    
    def execute_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行 SQL（无返回结果）"""
        try:
            with self._Session() as session:
                result = session.execute(text(sql), params or {})
                session.commit()
                
                return {
                    "rowcount": result.rowcount,
                    "status": "success",
                }
        except SQLAlchemyError as e:
            raise Exception(f"SQL 执行错误: {str(e)}")
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """插入单条数据"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f":{k}" for k in data.keys()])
        
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self._Session() as session:
                result = session.execute(text(sql), data)
                session.commit()
                
                return {
                    "status": "success",
                    "rowcount": result.rowcount,
                    "lastrowid": result.lastrowid if hasattr(result, 'lastrowid') else None,
                }
        except SQLAlchemyError as e:
            raise Exception(f"插入错误: {str(e)}")
    
    def bulk_insert(self, table: str, data: List[Dict[str, Any]], batch_size: int = 1000) -> Dict[str, Any]:
        """批量插入数据"""
        if not data:
            return {"status": "success", "rowcount": 0}
        
        columns = ", ".join(data[0].keys())
        
        total_rows = 0
        
        try:
            with self._Session() as session:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i+batch_size]
                    values = []
                    params = {}
                    
                    for idx, row in enumerate(batch):
                        row_placeholders = []
                        for key in row.keys():
                            param_key = f"{key}_{i}_{idx}"
                            row_placeholders.append(f":{param_key}")
                            params[param_key] = row[key]
                        values.append(f"({', '.join(row_placeholders)})")
                    
                    sql = f"INSERT INTO {table} ({columns}) VALUES {', '.join(values)}"
                    result = session.execute(text(sql), params)
                    total_rows += result.rowcount
                
                session.commit()
                
                return {
                    "status": "success",
                    "rowcount": total_rows,
                    "batches": (len(data) + batch_size - 1) // batch_size,
                }
        except SQLAlchemyError as e:
            raise Exception(f"批量插入错误: {str(e)}")
    
    def update(self, table: str, data: Dict[str, Any], where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """更新数据"""
        set_clause = ", ".join([f"{k} = :{k}" for k in data.keys()])
        
        sql = f"UPDATE {table} SET {set_clause}"
        params = data.copy()
        
        if where:
            where_clause = " AND ".join([f"{k} = :where_{k}" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            for k, v in where.items():
                params[f"where_{k}"] = v
        
        try:
            with self._Session() as session:
                result = session.execute(text(sql), params)
                session.commit()
                
                return {
                    "status": "success",
                    "rowcount": result.rowcount,
                }
        except SQLAlchemyError as e:
            raise Exception(f"更新错误: {str(e)}")
    
    def delete(self, table: str, where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """删除数据"""
        sql = f"DELETE FROM {table}"
        params = {}
        
        if where:
            where_clause = " AND ".join([f"{k} = :where_{k}" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            for k, v in where.items():
                params[f"where_{k}"] = v
        
        try:
            with self._Session() as session:
                result = session.execute(text(sql), params)
                session.commit()
                
                return {
                    "status": "success",
                    "rowcount": result.rowcount,
                }
        except SQLAlchemyError as e:
            raise Exception(f"删除错误: {str(e)}")
    
    def select(
        self,
        table: str,
        fields: Optional[List[str]] = None,
        where: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """查询数据"""
        select_fields = "*" if not fields else ", ".join(fields)
        
        sql = f"SELECT {select_fields} FROM {table}"
        params = {}
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        sql += " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        try:
            with self._Session() as session:
                result = session.execute(text(sql), params)
                columns = result.keys()
                rows = result.fetchall()
                
                return {
                    "columns": list(columns),
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "count": len(rows),
                    "limit": limit,
                    "offset": offset,
                }
        except SQLAlchemyError as e:
            raise Exception(f"查询错误: {str(e)}")


# 全局实例
mysql_service = MySQLService()
