import redis.asyncio as redis
from app.config import settings
from typing import Optional, List, Dict, Any
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }

    async def connect(self):
        """Redis 연결"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None

    async def get(self, key: str) -> Optional[str]:
        """캐시 조회 (히트율 추적)"""
        if not self.redis_client:
            self.stats['misses'] += 1
            return None
        try:
            value = await self.redis_client.get(key)
            if value:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
            return value
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            self.stats['misses'] += 1
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        """캐시 저장"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.set(key, value, ex=expire)
            self.stats['sets'] += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False

    async def delete(self, key: str):
        """캐시 삭제"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            self.stats['deletes'] += 1
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False

    async def delete_pattern(self, pattern: str):
        """패턴 매칭으로 캐시 일괄 삭제"""
        if not self.redis_client:
            return 0
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.stats['deletes'] += deleted
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {str(e)}")
            return 0

    async def mget(self, keys: List[str]) -> List[Optional[str]]:
        """여러 키 일괄 조회"""
        if not self.redis_client:
            return [None] * len(keys)
        try:
            values = await self.redis_client.mget(keys)
            for val in values:
                if val:
                    self.stats['hits'] += 1
                else:
                    self.stats['misses'] += 1
            return values
        except Exception as e:
            logger.error(f"Cache mget error: {str(e)}")
            return [None] * len(keys)

    async def mset(self, mapping: Dict[str, str], expire: int = 3600):
        """여러 키-값 일괄 저장"""
        if not self.redis_client:
            return False
        try:
            async with self.redis_client.pipeline() as pipe:
                for key, value in mapping.items():
                    pipe.set(key, value, ex=expire)
                await pipe.execute()
                self.stats['sets'] += len(mapping)
            return True
        except Exception as e:
            logger.error(f"Cache mset error: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """캐시 키 존재 여부 확인"""
        if not self.redis_client:
            return False
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {str(e)}")
            return False

    async def ttl(self, key: str) -> int:
        """캐시 TTL 조회 (초)"""
        if not self.redis_client:
            return -2
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL error: {str(e)}")
            return -2

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Redis 메모리 사용량 확인"""
        if not self.redis_client:
            return {}
        try:
            info = await self.redis_client.info('memory')
            return {
                'used_memory': info.get('used_memory', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'used_memory_peak': info.get('used_memory_peak', 0),
                'used_memory_peak_human': info.get('used_memory_peak_human', '0B'),
                'maxmemory': info.get('maxmemory', 0),
                'maxmemory_human': info.get('maxmemory_human', 'unlimited'),
            }
        except Exception as e:
            logger.error(f"Get memory stats error: {str(e)}")
            return {}

    def get_stats(self) -> Dict[str, Any]:
        """캐시 히트율 통계"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'sets': self.stats['sets'],
            'deletes': self.stats['deletes'],
            'total_requests': total_requests
        }

    def reset_stats(self):
        """통계 초기화"""
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }


# 싱글톤 인스턴스
cache_service = CacheService()
