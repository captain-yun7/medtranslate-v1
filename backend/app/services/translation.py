"""
Multi-Provider Translation Service
Supports OpenAI, Claude, Google, DeepL, and Mock providers
"""

from typing import Optional
import hashlib
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.services.cache import cache_service
from app.config import settings
from app.services.providers import (
    BaseTranslationProvider,
    OpenAIProvider,
    ClaudeProvider,
    MockProvider,
)

logger = logging.getLogger(__name__)


class TranslationService:
    """
    멀티 프로바이더 번역 서비스

    환경 변수로 번역 프로바이더를 선택할 수 있습니다:
    - TRANSLATION_PROVIDER: 'openai', 'claude', 'google', 'deepl', 'mock'
    - OPENAI_API_KEY: OpenAI API 키
    - ANTHROPIC_API_KEY: Claude API 키
    - OPENAI_MODEL: OpenAI 모델 (기본: gpt-3.5-turbo)
    """

    def __init__(self):
        self.medical_glossary = self._load_glossary()
        self.provider: Optional[BaseTranslationProvider] = None
        self._init_provider()

    def _load_glossary(self):
        """의료 용어집 로드"""
        return {
            "ko": {
                "예약": {"en": "appointment", "vi": "lịch hẹn", "ja": "予約", "zh": "预约", "th": "การนัดหมาย"},
                "진료": {"en": "consultation", "vi": "khám bệnh", "ja": "診察", "zh": "就诊", "th": "การตรวจรักษา"},
                "처방전": {"en": "prescription", "vi": "đơn thuốc", "ja": "処方箋", "zh": "处方", "th": "ใบสั่งยา"},
                "증상": {"en": "symptom", "vi": "triệu chứng", "ja": "症状", "zh": "症状", "th": "อาการ"},
                "통증": {"en": "pain", "vi": "đau", "ja": "痛み", "zh": "疼痛", "th": "ความเจ็บปวด"},
                "검사": {"en": "examination", "vi": "kiểm tra", "ja": "検査", "zh": "检查", "th": "การตรวจสอบ"},
                "수술": {"en": "surgery", "vi": "phẫu thuật", "ja": "手術", "zh": "手术", "th": "การผ่าตัด"},
                "입원": {"en": "hospitalization", "vi": "nhập viện", "ja": "入院", "zh": "住院", "th": "การเข้าพักรักษา"},
            }
        }

    def _init_provider(self):
        """프로바이더 초기화 (Factory Pattern)"""
        provider_name = getattr(settings, 'TRANSLATION_PROVIDER', 'mock').lower()

        logger.info(f"Initializing translation provider: {provider_name}")

        if provider_name == 'openai':
            self.provider = self._init_openai()
        elif provider_name == 'claude':
            self.provider = self._init_claude()
        elif provider_name == 'mock':
            self.provider = MockProvider(self.medical_glossary)
        else:
            logger.warning(f"Unknown provider '{provider_name}', falling back to mock")
            self.provider = MockProvider(self.medical_glossary)

        # Fallback to Mock if provider initialization failed
        if self.provider is None or not self.provider.is_available():
            logger.warning(f"Provider '{provider_name}' not available, using Mock provider")
            self.provider = MockProvider(self.medical_glossary)

        logger.info(f"Translation provider ready: {self.provider.name}")

    def _init_openai(self) -> Optional[OpenAIProvider]:
        """OpenAI 프로바이더 초기화"""
        try:
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key or api_key == "your-api-key-here":
                logger.warning("OpenAI API key not configured")
                return None

            model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)

            provider = OpenAIProvider(
                api_key=api_key,
                medical_glossary=self.medical_glossary,
                model=model,
                temperature=temperature
            )

            if provider.is_available():
                return provider
            return None

        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {e}")
            return None

    def _init_claude(self) -> Optional[ClaudeProvider]:
        """Claude 프로바이더 초기화"""
        try:
            api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
            if not api_key or api_key == "your-api-key-here":
                logger.warning("Anthropic API key not configured")
                return None

            model = getattr(settings, 'CLAUDE_MODEL', 'claude-sonnet-4-5-20250929')

            provider = ClaudeProvider(
                api_key=api_key,
                medical_glossary=self.medical_glossary,
                model=model
            )

            if provider.is_available():
                return provider
            return None

        except Exception as e:
            logger.error(f"Failed to initialize Claude provider: {e}")
            return None

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        AI 번역 (캐싱 포함, 에러 핸들링, Retry)

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어 코드
            target_lang: 타겟 언어 코드
            context: 컨텍스트 ('medical', 'general')

        Returns:
            번역된 텍스트
        """
        # 1. 캐시 확인
        cache_key = self._get_cache_key(text, source_lang, target_lang)
        cached = await cache_service.get(cache_key)
        if cached:
            logger.info(f"Cache hit for: {text[:30]}...")
            return cached

        # 2. AI 번역 (Retry 포함)
        try:
            translated = await self._translate_with_retry(
                text, source_lang, target_lang, context
            )

            # 3. 캐시 저장 (30일)
            await cache_service.set(cache_key, translated, expire=2592000)

            return translated

        except Exception as e:
            logger.error(f"Translation failed after retries: {str(e)}")
            # Fallback: Mock 번역 반환
            return self._get_fallback_translation(text, source_lang, target_lang)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((asyncio.TimeoutError, ConnectionError))
    )
    async def _translate_with_retry(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str
    ) -> str:
        """Retry 로직이 포함된 번역"""
        if self.provider is None:
            raise ValueError("Translation provider not initialized")

        return await self.provider.translate(text, source_lang, target_lang, context)

    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """캐시 키 생성"""
        # 프로바이더 이름도 캐시 키에 포함 (프로바이더별로 다른 번역)
        provider_name = self.provider.name if self.provider else "unknown"
        content = f"{provider_name}:{text}:{source_lang}:{target_lang}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        return f"trans:{hash_key}"

    def _get_fallback_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Fallback 번역 (에러 발생 시)"""
        # Mock 프로바이더로 fallback
        mock_provider = MockProvider(self.medical_glossary)
        try:
            # Sync wrapper for async call
            import asyncio
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                mock_provider.translate(text, source_lang, target_lang)
            )
        except:
            return f"[Translation Failed] {text}"

    def get_provider_info(self) -> dict:
        """현재 프로바이더 정보 반환"""
        if self.provider is None:
            return {"provider": "None", "available": False}

        return {
            "provider": self.provider.name,
            "available": self.provider.is_available(),
            "type": type(self.provider).__name__
        }


# 싱글톤 인스턴스
translation_service = TranslationService()
