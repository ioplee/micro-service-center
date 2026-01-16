from typing import Optional, List, Dict, Any
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    Index,
)

from common import get_settings


settings = get_settings()


class MilvusService:
    """Milvus 向量数据库服务"""
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """建立连接"""
        try:
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port,
                user=settings.milvus_user,
                password=settings.milvus_password,
            )
            
            print("✓ Milvus 连接成功")
        except Exception as e:
            print(f"✗ Milvus 连接失败: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            return {
                "status": "healthy",
                "database": "Milvus",
                "connected": connections.has_connection("default"),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "Milvus",
                "error": str(e),
            }
    
    def get_collections(self) -> List[str]:
        """获取所有集合"""
        try:
            return utility.list_collections()
        except Exception as e:
            raise Exception(f"获取集合列表错误: {str(e)}")
    
    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        metric_type: str = "L2",
        index_type: str = "IVF_FLAT",
        index_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """创建集合"""
        try:
            fields = [
                FieldSchema(
                    name="id",
                    dtype=DataType.INT64,
                    is_primary=True,
                    auto_id=True,
                ),
                FieldSchema(
                    name="vector",
                    dtype=DataType.FLOAT_VECTOR,
                    dim=dimension,
                ),
            ]
            
            schema = CollectionSchema(
                fields=fields,
                description=f"Collection: {collection_name}",
            )
            
            collection = Collection(
                name=collection_name,
                schema=schema,
                using="default",
            )
            
            # 创建索引
            default_index_params = {
                "metric_type": metric_type,
                "index_type": index_type,
                "params": {"nlist": 1024},
            }
            
            collection.create_index(
                field_name="vector",
                index_params=index_params or default_index_params,
            )
            
            return {
                "status": "success",
                "message": f"集合 {collection_name} 已创建",
            }
        except Exception as e:
            raise Exception(f"创建集合错误: {str(e)}")
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """删除集合"""
        try:
            utility.drop_collection(collection_name)
            return {
                "status": "success",
                "message": f"集合 {collection_name} 已删除",
            }
        except Exception as e:
            raise Exception(f"删除集合错误: {str(e)}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            collection = Collection(collection_name)
            
            return {
                "name": collection.name,
                "description": collection.description,
                "is_empty": collection.is_empty,
                "num_entities": collection.num_entities,
                "indexes": [
                    {
                        "field_name": idx.field_name,
                        "index_name": idx.index_name,
                        "index_type": idx.index_type,
                    }
                    for idx in collection.indexes
                ],
            }
        except Exception as e:
            raise Exception(f"获取集合信息错误: {str(e)}")
    
    def insert(
        self,
        collection_name: str,
        data: List[List[float]],
        ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """插入向量"""
        try:
            collection = Collection(collection_name)
            
            if ids:
                result = collection.insert([ids, data])
            else:
                result = collection.insert([data])
            
            collection.flush()
            
            return {
                "status": "success",
                "inserted_count": result.insert_count,
                "ids": result.primary_keys,
            }
        except Exception as e:
            raise Exception(f"插入向量错误: {str(e)}")
    
    def search(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        limit: int = 10,
        expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """向量搜索"""
        try:
            collection = Collection(collection_name)
            collection.load()
            
            search_params = {
                "metric_type": "L2",
                "params": {"nprobe": 10},
            }
            
            results = collection.search(
                data=query_vectors,
                anns_field="vector",
                param=search_params,
                limit=limit,
                expr=expr,
                output_fields=output_fields,
            )
            
            collection.release()
            
            search_results = []
            for result in results:
                hits = []
                for hit in result:
                    hits.append({
                        "id": hit.id,
                        "distance": hit.distance,
                        "entity": hit.entity,
                    })
                search_results.append({
                    "query_index": result.query_index,
                    "hits": hits,
                })
            
            return search_results
        except Exception as e:
            raise Exception(f"向量搜索错误: {str(e)}")
    
    def query(
        self,
        collection_name: str,
        expr: str,
        output_fields: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """查询向量"""
        try:
            collection = Collection(collection_name)
            collection.load()
            
            results = collection.query(
                expr=expr,
                output_fields=output_fields,
                limit=limit,
            )
            
            collection.release()
            
            return results
        except Exception as e:
            raise Exception(f"查询向量错误: {str(e)}")
    
    def delete(self, collection_name: str, expr: str) -> Dict[str, Any]:
        """删除向量"""
        try:
            collection = Collection(collection_name)
            
            result = collection.delete(expr=expr)
            collection.flush()
            
            return {
                "status": "success",
                "deleted_count": result.delete_count,
            }
        except Exception as e:
            raise Exception(f"删除向量错误: {str(e)}")
    
    def count(self, collection_name: str) -> int:
        """统计向量数量"""
        try:
            collection = Collection(collection_name)
            return collection.num_entities
        except Exception as e:
            raise Exception(f"统计向量数量错误: {str(e)}")
    
    def load(self, collection_name: str) -> Dict[str, Any]:
        """加载集合到内存"""
        try:
            collection = Collection(collection_name)
            collection.load()
            
            return {
                "status": "success",
                "message": f"集合 {collection_name} 已加载到内存",
            }
        except Exception as e:
            raise Exception(f"加载集合错误: {str(e)}")
    
    def release(self, collection_name: str) -> Dict[str, Any]:
        """释放集合内存"""
        try:
            collection = Collection(collection_name)
            collection.release()
            
            return {
                "status": "success",
                "message": f"集合 {collection_name} 内存已释放",
            }
        except Exception as e:
            raise Exception(f"释放集合内存错误: {str(e)}")
    
    def create_index(
        self,
        collection_name: str,
        index_type: str = "IVF_FLAT",
        index_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """创建索引"""
        try:
            collection = Collection(collection_name)
            
            default_index_params = {
                "metric_type": "L2",
                "index_type": index_type,
                "params": {"nlist": 1024},
            }
            
            collection.create_index(
                field_name="vector",
                index_params=index_params or default_index_params,
            )
            
            return {
                "status": "success",
                "message": f"索引已创建",
            }
        except Exception as e:
            raise Exception(f"创建索引错误: {str(e)}")
    
    def drop_index(self, collection_name: str) -> Dict[str, Any]:
        """删除索引"""
        try:
            collection = Collection(collection_name)
            collection.drop_index()
            
            return {
                "status": "success",
                "message": f"索引已删除",
            }
        except Exception as e:
            raise Exception(f"删除索引错误: {str(e)}")


milvus_service = MilvusService()
