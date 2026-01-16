from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings

from common import get_settings


settings = get_settings()


class ChromaDBService:
    """ChromaDB 向量数据库服务"""
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """建立连接"""
        try:
            self._client = chromadb.PersistentClient(
                path=settings.chromadb_path,
            )
            
            print("✓ ChromaDB 连接成功")
        except Exception as e:
            print(f"✗ ChromaDB 连接失败: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            collections = self._client.list_collections()
            return {
                "status": "healthy",
                "database": "ChromaDB",
                "collections_count": len(collections),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "ChromaDB",
                "error": str(e),
            }
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """获取所有集合"""
        try:
            collections = self._client.list_collections()
            return [
                {
                    "name": col.name,
                    "id": col.id,
                    "metadata": col.metadata,
                    "count": col.count(),
                }
                for col in collections
            ]
        except Exception as e:
            raise Exception(f"获取集合列表错误: {str(e)}")
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """创建集合"""
        try:
            collection = self._client.create_collection(
                name=name,
                metadata=metadata,
            )
            
            return {
                "status": "success",
                "message": f"集合 {name} 已创建",
                "collection": {
                    "name": collection.name,
                    "id": collection.id,
                    "metadata": collection.metadata,
                },
            }
        except Exception as e:
            raise Exception(f"创建集合错误: {str(e)}")
    
    def delete_collection(self, name: str) -> Dict[str, Any]:
        """删除集合"""
        try:
            self._client.delete_collection(name)
            return {
                "status": "success",
                "message": f"集合 {name} 已删除",
            }
        except Exception as e:
            raise Exception(f"删除集合错误: {str(e)}")
    
    def get_collection(self, name: str) -> Optional[Dict[str, Any]]:
        """获取集合"""
        try:
            collection = self._client.get_collection(name)
            
            return {
                "name": collection.name,
                "id": collection.id,
                "metadata": collection.metadata,
                "count": collection.count(),
            }
        except Exception as e:
            raise Exception(f"获取集合错误: {str(e)}")
    
    def add(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """添加文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings,
            )
            
            return {
                "status": "success",
                "message": f"已添加 {len(documents)} 个文档",
            }
        except Exception as e:
            raise Exception(f"添加文档错误: {str(e)}")
    
    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """查询文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=include or ["documents", "metadatas", "distances"],
            )
            
            return results
        except Exception as e:
            raise Exception(f"查询文档错误: {str(e)}")
    
    def get(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """获取文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            results = collection.get(
                ids=ids,
                where=where,
                where_document=where_document,
                include=include or ["documents", "metadatas"],
                limit=limit,
            )
            
            return results
        except Exception as e:
            raise Exception(f"获取文档错误: {str(e)}")
    
    def update(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """更新文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            collection.update(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
            
            return {
                "status": "success",
                "message": f"已更新 {len(ids)} 个文档",
            }
        except Exception as e:
            raise Exception(f"更新文档错误: {str(e)}")
    
    def upsert(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
    ) -> Dict[str, Any]:
        """插入或更新文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings,
            )
            
            return {
                "status": "success",
                "message": f"已插入或更新 {len(documents)} 个文档",
            }
        except Exception as e:
            raise Exception(f"插入或更新文档错误: {str(e)}")
    
    def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """删除文档"""
        try:
            collection = self._client.get_collection(collection_name)
            
            collection.delete(
                ids=ids,
                where=where,
                where_document=where_document,
            )
            
            return {
                "status": "success",
                "message": "文档已删除",
            }
        except Exception as e:
            raise Exception(f"删除文档错误: {str(e)}")
    
    def count(self, collection_name: str) -> int:
        """统计文档数量"""
        try:
            collection = self._client.get_collection(collection_name)
            return collection.count()
        except Exception as e:
            raise Exception(f"统计文档数量错误: {str(e)}")
    
    def modify(
        self,
        collection_name: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """修改集合"""
        try:
            collection = self._client.get_collection(collection_name)
            
            collection.modify(
                name=name,
                metadata=metadata,
            )
            
            return {
                "status": "success",
                "message": "集合已修改",
            }
        except Exception as e:
            raise Exception(f"修改集合错误: {str(e)}")


chromadb_service = ChromaDBService()
