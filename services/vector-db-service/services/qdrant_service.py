from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from common import get_settings


settings = get_settings()


class QdrantService:
    """Qdrant 向量数据库服务"""
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """建立连接"""
        try:
            self._client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
            )
            
            print("✓ Qdrant 连接成功")
        except Exception as e:
            print(f"✗ Qdrant 连接失败: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            info = self._client.get_cluster_info()
            return {
                "status": "healthy",
                "database": "Qdrant",
                "version": info.version,
                "peer_id": info.peer_id,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "Qdrant",
                "error": str(e),
            }
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """获取所有集合"""
        try:
            collections = self._client.get_collections()
            return [
                {
                    "name": c.name,
                    "vectors_count": c.vectors_count,
                    "points_count": c.points_count,
                }
                for c in collections.collections
            ]
        except Exception as e:
            raise Exception(f"获取集合列表错误: {str(e)}")
    
    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
        shard_number: Optional[int] = None,
        replication_factor: Optional[int] = None,
    ) -> Dict[str, Any]:
        """创建集合"""
        try:
            distance_map = {
                "Cosine": Distance.COSINE,
                "Euclid": Distance.EUCLID,
                "Dot": Distance.DOT,
            }
            
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE),
                ),
                shard_number=shard_number,
                replication_factor=replication_factor,
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
            self._client.delete_collection(collection_name=collection_name)
            return {
                "status": "success",
                "message": f"集合 {collection_name} 已删除",
            }
        except Exception as e:
            raise Exception(f"删除集合错误: {str(e)}")
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            info = self._client.get_collection(collection_name=collection_name)
            return {
                "name": info.name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status.name,
                "vectors_config": {
                    k: {
                        "size": v.size,
                        "distance": v.distance.name,
                    }
                    for k, v in info.config.params.vectors.items()
                },
            }
        except Exception as e:
            raise Exception(f"获取集合信息错误: {str(e)}")
    
    def insert_points(self, collection_name: str, points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """插入向量点"""
        try:
            point_structs = []
            for point in points:
                point_id = point.get("id")
                vector = point.get("vector")
                payload = point.get("payload", {})
                
                point_structs.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                )
            
            operation_info = self._client.upsert(
                collection_name=collection_name,
                points=point_structs,
            )
            
            return {
                "status": "success",
                "operation_id": operation_info.operation_id,
                "inserted_count": len(points),
            }
        except Exception as e:
            raise Exception(f"插入向量点错误: {str(e)}")
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        offset: int = 0,
        filter: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> List[Dict[str, Any]]:
        """向量搜索"""
        try:
            results = self._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                query_filter=models.Filter(**filter) if filter else None,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                    "vector": hit.vector if with_vectors else None,
                }
                for hit in results
            ]
        except Exception as e:
            raise Exception(f"向量搜索错误: {str(e)}")
    
    def query(
        self,
        collection_name: str,
        query: str,
        limit: int = 10,
        offset: int = 0,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """向量查询"""
        try:
            results = self._client.query_points(
                collection_name=collection_name,
                query=query,
                limit=limit,
                offset=offset,
                query_filter=models.Filter(**filter) if filter else None,
            )
            
            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
                for hit in results
            ]
        except Exception as e:
            raise Exception(f"向量查询错误: {str(e)}")
    
    def get_point(
        self,
        collection_name: str,
        point_id: int,
        with_payload: bool = True,
        with_vector: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """获取向量点"""
        try:
            result = self._client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=with_payload,
                with_vectors=with_vector,
            )
            
            if result:
                hit = result[0]
                return {
                    "id": hit.id,
                    "payload": hit.payload,
                    "vector": hit.vector if with_vector else None,
                }
            
            return None
        except Exception as e:
            raise Exception(f"获取向量点错误: {str(e)}")
    
    def update_point(
        self,
        collection_name: str,
        point_id: int,
        payload: Optional[Dict[str, Any]] = None,
        vector: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """更新向量点"""
        try:
            self._client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload,
                    )
                ],
            )
            
            return {
                "status": "success",
                "message": f"向量点 {point_id} 已更新",
            }
        except Exception as e:
            raise Exception(f"更新向量点错误: {str(e)}")
    
    def delete_point(self, collection_name: str, point_id: int) -> Dict[str, Any]:
        """删除向量点"""
        try:
            self._client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=[point_id]
                ),
            )
            
            return {
                "status": "success",
                "message": f"向量点 {point_id} 已删除",
            }
        except Exception as e:
            raise Exception(f"删除向量点错误: {str(e)}")
    
    def delete_points(self, collection_name: str, point_ids: List[int]) -> Dict[str, Any]:
        """批量删除向量点"""
        try:
            self._client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(
                    points=point_ids
                ),
            )
            
            return {
                "status": "success",
                "message": f"已删除 {len(point_ids)} 个向量点",
            }
        except Exception as e:
            raise Exception(f"批量删除向量点错误: {str(e)}")
    
    def scroll(
        self,
        collection_name: str,
        limit: int = 100,
        offset: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> Dict[str, Any]:
        """滚动查询"""
        try:
            points, next_offset = self._client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                scroll_filter=models.Filter(**filter) if filter else None,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            
            return {
                "points": [
                    {
                        "id": point.id,
                        "payload": point.payload,
                        "vector": point.vector if with_vectors else None,
                    }
                    for point in points
                ],
                "next_offset": next_offset,
                "count": len(points),
            }
        except Exception as e:
            raise Exception(f"滚动查询错误: {str(e)}")
    
    def set_alias(self, collection_name: str, alias_name: str) -> Dict[str, Any]:
        """设置集合别名"""
        try:
            self._client.create_alias(
                collection_name=collection_name,
                alias_name=alias_name,
            )
            
            return {
                "status": "success",
                "message": f"别名 {alias_name} 已设置",
            }
        except Exception as e:
            raise Exception(f"设置别名错误: {str(e)}")
    
    def delete_alias(self, alias_name: str) -> Dict[str, Any]:
        """删除集合别名"""
        try:
            self._client.delete_alias(alias_name=alias_name)
            
            return {
                "status": "success",
                "message": f"别名 {alias_name} 已删除",
            }
        except Exception as e:
            raise Exception(f"删除别名错误: {str(e)}")


qdrant_service = QdrantService()
