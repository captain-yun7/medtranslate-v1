import redis.asyncio as redis
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

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
        """캐시 조회"""
        if not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(self, key: str, value: str, expire: int = 3600):
        """캐시 저장"""
        if not self.redis_client:
            return False
        try:
            await self.redis_client.set(key, value, ex=expire)
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
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False


# 싱글톤 인스턴스
cache_service = CacheService()
