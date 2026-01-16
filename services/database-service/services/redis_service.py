from typing import Optional, List, Dict, Any
import json
import redis

from common import get_settings


settings = get_settings()


class RedisService:
    """Redis 数据库服务"""
    
    def __init__(self):
        self._client = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            
            # 测试连接
            self._client.ping()
            print("✓ Redis 连接成功")
        except Exception as e:
            print(f"✗ Redis 连接失败: {str(e)}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            self._client.ping()
            info = self._client.info()
            return {
                "status": "healthy",
                "database": "Redis",
                "version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "database": "Redis",
                "error": str(e),
            }
    
    def get_info(self) -> Dict[str, Any]:
        """获取 Redis 信息"""
        try:
            return self._client.info()
        except Exception as e:
            raise Exception(f"获取信息错误: {str(e)}")
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置键值对"""
        try:
            # 序列化复杂类型
            if not isinstance(value, (str, int, float, bytes)):
                value = json.dumps(value, ensure_ascii=False)
            
            if expire:
                self._client.setex(key, expire, value)
            else:
                self._client.set(key, value)
            
            return True
        except Exception as e:
            raise Exception(f"设置键值错误: {str(e)}")
    
    def get(self, key: str) -> Any:
        """获取键值"""
        try:
            value = self._client.get(key)
            
            if value is None:
                return None
            
            # 尝试反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            raise Exception(f"获取键值错误: {str(e)}")
    
    def set_multiple(self, data: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """批量设置键值对"""
        try:
            pipe = self._client.pipeline()
            
            for key, value in data.items():
                if not isinstance(value, (str, int, float, bytes)):
                    value = json.dumps(value, ensure_ascii=False)
                
                if expire:
                    pipe.setex(key, expire, value)
                else:
                    pipe.set(key, value)
            
            pipe.execute()
            return True
        except Exception as e:
            raise Exception(f"批量设置键值错误: {str(e)}")
    
    def get_multiple(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取键值"""
        try:
            values = self._client.mget(keys)
            
            result = {}
            for key, value in zip(keys, values):
                if value is None:
                    result[key] = None
                    continue
                
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            
            return result
        except Exception as e:
            raise Exception(f"批量获取键值错误: {str(e)}")
    
    def delete(self, keys: List[str]) -> int:
        """删除键"""
        try:
            return self._client.delete(*keys)
        except Exception as e:
            raise Exception(f"删除键错误: {str(e)}")
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self._client.exists(key) > 0
        except Exception as e:
            raise Exception(f"检查键是否存在错误: {str(e)}")
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        try:
            return self._client.expire(key, seconds)
        except Exception as e:
            raise Exception(f"设置过期时间错误: {str(e)}")
    
    def ttl(self, key: str) -> int:
        """获取键剩余过期时间"""
        try:
            return self._client.ttl(key)
        except Exception as e:
            raise Exception(f"获取过期时间错误: {str(e)}")
    
    def hset(self, key: str, field: str, value: Any) -> int:
        """设置哈希字段"""
        try:
            if not isinstance(value, (str, int, float, bytes)):
                value = json.dumps(value, ensure_ascii=False)
            
            return self._client.hset(key, field, value)
        except Exception as e:
            raise Exception(f"设置哈希字段错误: {str(e)}")
    
    def hget(self, key: str, field: Optional[str] = None) -> Any:
        """获取哈希字段"""
        try:
            if field:
                value = self._client.hget(key, field)
                if value is None:
                    return None
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                # 获取整个哈希
                hash_data = self._client.hgetall(key)
                result = {}
                for k, v in hash_data.items():
                    try:
                        result[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        result[k] = v
                return result
        except Exception as e:
            raise Exception(f"获取哈希字段错误: {str(e)}")
    
    def hmset(self, key: str, data: Dict[str, Any]) -> bool:
        """批量设置哈希字段"""
        try:
            processed_data = {}
            for field, value in data.items():
                if not isinstance(value, (str, int, float, bytes)):
                    value = json.dumps(value, ensure_ascii=False)
                processed_data[field] = value
            
            self._client.hset(key, mapping=processed_data)
            return True
        except Exception as e:
            raise Exception(f"批量设置哈希字段错误: {str(e)}")
    
    def lpush(self, key: str, values: List[Any]) -> int:
        """左侧插入列表"""
        try:
            processed_values = []
            for v in values:
                if not isinstance(v, (str, int, float, bytes)):
                    v = json.dumps(v, ensure_ascii=False)
                processed_values.append(v)
            
            return self._client.lpush(key, *processed_values)
        except Exception as e:
            raise Exception(f"左侧插入列表错误: {str(e)}")
    
    def rpush(self, key: str, values: List[Any]) -> int:
        """右侧插入列表"""
        try:
            processed_values = []
            for v in values:
                if not isinstance(v, (str, int, float, bytes)):
                    v = json.dumps(v, ensure_ascii=False)
                processed_values.append(v)
            
            return self._client.rpush(key, *processed_values)
        except Exception as e:
            raise Exception(f"右侧插入列表错误: {str(e)}")
    
    def lpop(self, key: str, count: int = 1) -> Any:
        """左侧弹出列表"""
        try:
            if count == 1:
                value = self._client.lpop(key)
                if value is None:
                    return None
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                values = self._client.lpop(key, count)
                result = []
                for v in values:
                    try:
                        result.append(json.loads(v))
                    except (json.JSONDecodeError, TypeError):
                        result.append(v)
                return result
        except Exception as e:
            raise Exception(f"左侧弹出列表错误: {str(e)}")
    
    def rpop(self, key: str, count: int = 1) -> Any:
        """右侧弹出列表"""
        try:
            if count == 1:
                value = self._client.rpop(key)
                if value is None:
                    return None
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            else:
                values = self._client.rpop(key, count)
                result = []
                for v in values:
                    try:
                        result.append(json.loads(v))
                    except (json.JSONDecodeError, TypeError):
                        result.append(v)
                return result
        except Exception as e:
            raise Exception(f"右侧弹出列表错误: {str(e)}")
    
    def sadd(self, key: str, values: List[Any]) -> int:
        """添加集合元素"""
        try:
            processed_values = []
            for v in values:
                if not isinstance(v, (str, int, float, bytes)):
                    v = json.dumps(v, ensure_ascii=False)
                processed_values.append(v)
            
            return self._client.sadd(key, *processed_values)
        except Exception as e:
            raise Exception(f"添加集合元素错误: {str(e)}")
    
    def smembers(self, key: str) -> List[Any]:
        """获取集合所有元素"""
        try:
            members = self._client.smembers(key)
            result = []
            for v in members:
                try:
                    result.append(json.loads(v))
                except (json.JSONDecodeError, TypeError):
                    result.append(v)
            return result
        except Exception as e:
            raise Exception(f"获取集合元素错误: {str(e)}")
    
    def zadd(self, key: str, members: Dict[str, float]) -> int:
        """添加有序集合元素"""
        try:
            return self._client.zadd(key, members)
        except Exception as e:
            raise Exception(f"添加有序集合元素错误: {str(e)}")
    
    def zrange(self, key: str, start: int, end: int, with_scores: bool = False) -> Any:
        """获取有序集合范围"""
        try:
            result = self._client.zrange(key, start, end, withscores=with_scores)
            
            if with_scores:
                processed = []
                for member, score in result:
                    try:
                        member = json.loads(member)
                    except (json.JSONDecodeError, TypeError):
                        pass
                    processed.append({"member": member, "score": score})
                return processed
            else:
                processed = []
                for member in result:
                    try:
                        processed.append(json.loads(member))
                    except (json.JSONDecodeError, TypeError):
                        processed.append(member)
                return processed
        except Exception as e:
            raise Exception(f"获取有序集合范围错误: {str(e)}")
    
    def publish(self, channel: str, message: Any) -> int:
        """发布消息"""
        try:
            if not isinstance(message, (str, int, float, bytes)):
                message = json.dumps(message, ensure_ascii=False)
            
            return self._client.publish(channel, message)
        except Exception as e:
            raise Exception(f"发布消息错误: {str(e)}")
    
    def transaction(self, commands: List[List[str]]) -> List[Any]:
        """执行事务"""
        try:
            pipe = self._client.pipeline()
            
            for cmd in commands:
                if not cmd:
                    continue
                method = cmd[0]
                args = cmd[1:]
                
                # 序列化参数
                processed_args = []
                for arg in args:
                    if not isinstance(arg, (str, int, float, bytes)):
                        arg = json.dumps(arg, ensure_ascii=False)
                    processed_args.append(arg)
                
                getattr(pipe, method)(*processed_args)
            
            result = pipe.execute()
            
            # 反序列化结果
            processed_result = []
            for item in result:
                if isinstance(item, bytes):
                    try:
                        processed_result.append(json.loads(item))
                    except (json.JSONDecodeError, TypeError):
                        processed_result.append(item)
                else:
                    processed_result.append(item)
            
            return processed_result
        except Exception as e:
            raise Exception(f"执行事务错误: {str(e)}")
    
    def eval(self, script: str, keys: List[str], args: List[Any]) -> Any:
        """执行 Lua 脚本"""
        try:
            processed_args = []
            for arg in args:
                if not isinstance(arg, (str, int, float, bytes)):
                    arg = json.dumps(arg, ensure_ascii=False)
                processed_args.append(arg)
            
            result = self._client.eval(script, len(keys), *keys, *processed_args)
            
            if isinstance(result, bytes):
                try:
                    return json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    return result
            
            return result
        except Exception as e:
            raise Exception(f"执行 Lua 脚本错误: {str(e)}")


# 全局实例
redis_service = RedisService()
