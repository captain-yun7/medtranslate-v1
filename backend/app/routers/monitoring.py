from fastapi import APIRouter
from app.services.cache import cache_service
from app.services.translation import translation_service

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/cache/stats")
async def get_cache_stats():
    """
    캐시 히트율 통계 조회
    """
    return cache_service.get_stats()


@router.get("/cache/memory")
async def get_cache_memory():
    """
    Redis 메모리 사용량 조회
    """
    return await cache_service.get_memory_stats()


@router.post("/cache/stats/reset")
async def reset_cache_stats():
    """
    캐시 통계 초기화
    """
    cache_service.reset_stats()
    return {"message": "Cache stats reset successfully"}


@router.get("/translation/provider")
async def get_translation_provider():
    """
    현재 사용 중인 번역 프로바이더 정보 조회
    """
    return translation_service.get_provider_info()
