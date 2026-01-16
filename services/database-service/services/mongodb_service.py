from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId, json_util
import json

from common import get_settings


settings = get_settings()


class MongoDBService:
    """MongoDB 数据库服务"""
    
    def __init__(self):
        self._client = None
        self._db = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            if settings.mongodb_user and settings.mongodb_password:
                connection_string = (
                    f"mongodb://{settings.mongodb_user}:{settings.mongodb_password}@"
                    f"{settings.mongodb_host}:{settings.mongodb_port}/"
                    f"?authSource={settings.mongodb_db}"
                )
            else:
                connection_string = (
                    f"mongodb://{settings.mongodb_host}:{settings.mongodb_port}/"
                )
            
            self._client = AsyncIOMotorClient(
                connection_string,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=5000,
            )
            self._db = self._client[settings.mongodb_db]
            
            print("✓ MongoDB 连接成功")
        except Exception as e:
            print(f"✗ MongoDB 连接失败: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            await self._client.admin.command("ping")
            server_info = await self._client.server_info()
            return {
                "status": "healthy",
                "database": "MongoDB",
                "version": server_info.get("version", "unknown"),
                "connection": "ok",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "MongoDB",
                "error": str(e),
            }
    
    async def get_collections(self) -> List[str]:
        """获取所有集合"""
        collections = await self._db.list_collection_names()
        return collections
    
    async def find(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0,
        sort: Optional[List[List]] = None,
    ) -> Dict[str, Any]:
        """查询文档"""
        try:
            coll = self._db[collection]
            query = coll.find(filter or {}, projection or {})
            
            if sort:
                query = query.sort(sort)
            
            query = query.skip(skip).limit(limit)
            
            cursor = await query.to_list(length=limit)
            
            # 转换 ObjectId
            for doc in cursor:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            
            return {
                "data": cursor,
                "count": len(cursor),
                "limit": limit,
                "skip": skip,
            }
        except Exception as e:
            raise Exception(f"查询错误: {str(e)}")
    
    async def find_one(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """查询单个文档"""
        try:
            coll = self._db[collection]
            doc = await coll.find_one(filter or {}, projection or {})
            
            if doc and "_id" in doc:
                doc["_id"] = str(doc["_id"])
            
            return doc
        except Exception as e:
            raise Exception(f"查询单个文档错误: {str(e)}")
    
    async def insert(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """插入单个文档"""
        try:
            coll = self._db[collection]
            result = await coll.insert_one(data)
            
            return {
                "status": "success",
                "inserted_id": str(result.inserted_id),
            }
        except Exception as e:
            raise Exception(f"插入错误: {str(e)}")
    
    async def insert_many(self, collection: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量插入文档"""
        try:
            coll = self._db[collection]
            result = await coll.insert_many(data)
            
            return {
                "status": "success",
                "inserted_count": len(result.inserted_ids),
                "inserted_ids": [str(id) for id in result.inserted_ids],
            }
        except Exception as e:
            raise Exception(f"批量插入错误: {str(e)}")
    
    async def update(
        self,
        collection: str,
        filter: Dict[str, Any],
        data: Dict[str, Any],
        upsert: bool = False,
        multi: bool = False,
    ) -> Dict[str, Any]:
        """更新文档"""
        try:
            coll = self._db[collection]
            
            # 转换为 $set
            if not data.get("$set"):
                data = {"$set": data}
            
            if multi:
                result = await coll.update_many(filter, data, upsert=upsert)
            else:
                result = await coll.update_one(filter, data, upsert=upsert)
            
            return {
                "status": "success",
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None,
            }
        except Exception as e:
            raise Exception(f"更新错误: {str(e)}")
    
    async def delete(
        self,
        collection: str,
        filter: Dict[str, Any],
        multi: bool = False,
    ) -> Dict[str, Any]:
        """删除文档"""
        try:
            coll = self._db[collection]
            
            if multi:
                result = await coll.delete_many(filter)
            else:
                result = await coll.delete_one(filter)
            
            return {
                "status": "success",
                "deleted_count": result.deleted_count,
            }
        except Exception as e:
            raise Exception(f"删除错误: {str(e)}")
    
    async def aggregate(
        self,
        collection: str,
        pipeline: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """聚合查询"""
        try:
            coll = self._db[collection]
            cursor = coll.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            
            # 转换 ObjectId
            for doc in result:
                if "_id" in doc:
                    if isinstance(doc["_id"], ObjectId):
                        doc["_id"] = str(doc["_id"])
            
            return result
        except Exception as e:
            raise Exception(f"聚合查询错误: {str(e)}")
    
    async def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """统计文档数量"""
        try:
            coll = self._db[collection]
            count = await coll.count_documents(filter or {})
            return count
        except Exception as e:
            raise Exception(f"统计错误: {str(e)}")
    
    async def drop_collection(self, collection: str) -> Dict[str, Any]:
        """删除集合"""
        try:
            await self._db[collection].drop()
            return {"status": "success", "message": f"集合 {collection} 已删除"}
        except Exception as e:
            raise Exception(f"删除集合错误: {str(e)}")


# 全局实例
mongodb_service = MongoDBService()
