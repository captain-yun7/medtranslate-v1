from anthropic import AsyncAnthropic
from typing import Optional
import hashlib
from app.services.cache import cache_service
from app.config import settings
import logging
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class TranslationService:
    def __init__(self):
        self.claude = None
        self.medical_glossary = self._load_glossary()

    def _init_claude(self):
        """Lazy initialization of Claude client"""
        if self.claude is None:
            try:
                # API 키 확인
                if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your-api-key-here":
                    logger.warning("Anthropic API key not configured - using mock translation")
                    return False

                self.claude = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                return True
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                return False
        return True

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

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        AI 번역 (캐싱 포함, 에러 핸들링, Retry)
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
            # Fallback: 기본 번역 반환
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
        return await self._translate_with_claude(text, source_lang, target_lang, context)

    async def _translate_with_claude(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str
    ) -> str:
        """Claude API로 번역"""

        # Initialize Claude client if not already done
        if not self._init_claude():
            # API 키가 없으면 mock 번역 반환
            return self._get_mock_translation(text, source_lang, target_lang)

        # 용어집 컨텍스트 생성
        glossary_context = self._create_glossary_context(source_lang, target_lang)

        # 언어별 이름 매핑
        lang_names = {
            'ko': '한국어',
            'en': 'English',
            'ja': '日本語',
            'zh': '中文',
            'vi': 'Tiếng Việt',
            'th': 'ภาษาไทย'
        }

        prompt = f"""당신은 의료 전문 통역사입니다.
다음 의료 상담 메시지를 {lang_names.get(target_lang, target_lang)}로 정확하게 번역해주세요.

원문 언어: {lang_names.get(source_lang, source_lang)}
원문: {text}

의료 용어 참고:
{glossary_context}

번역 시 주의사항:
1. 의료 용어는 정확하게 번역
2. 환자/의료진의 의도와 감정을 정확히 전달
3. 격식있고 공손한 표현 사용
4. 증상이나 통증 표현은 명확하게 번역
5. 문화적 차이를 고려한 자연스러운 표현

번역문만 출력하세요. 설명이나 주석 없이 번역 결과만 제공하세요."""

        message = await self.claude.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text.strip()

    def _create_glossary_context(self, source_lang: str, target_lang: str) -> str:
        """용어집 컨텍스트 생성"""
        if source_lang not in self.medical_glossary and target_lang not in self.medical_glossary:
            return ""

        context_lines = []

        # 한국어 기준으로 용어집 생성
        if source_lang == 'ko':
            for ko_term, translations in list(self.medical_glossary['ko'].items())[:20]:
                if target_lang in translations:
                    target_term = translations[target_lang]
                    context_lines.append(f"- {ko_term} → {target_term}")
        elif target_lang == 'ko':
            for ko_term, translations in list(self.medical_glossary['ko'].items())[:20]:
                if source_lang in translations:
                    source_term = translations[source_lang]
                    context_lines.append(f"- {source_term} → {ko_term}")

        return "\n".join(context_lines)

    def _get_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """캐시 키 생성"""
        content = f"{text}:{source_lang}:{target_lang}"
        hash_key = hashlib.md5(content.encode()).hexdigest()
        return f"trans:{hash_key}"

    def _get_mock_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Mock 번역 (API 키가 없을 때)"""
        lang_names = {
            'ko': 'Korean',
            'en': 'English',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'vi': 'Vietnamese',
            'th': 'Thai'
        }
        return f"[MOCK] {text} (translated from {lang_names.get(source_lang, source_lang)} to {lang_names.get(target_lang, target_lang)})"

    def _get_fallback_translation(self, text: str, source_lang: str, target_lang: str) -> str:
        """Fallback 번역 (에러 발생 시)"""
        # 용어집에서 직접 번역 시도
        if source_lang == 'ko' and source_lang in self.medical_glossary:
            for ko_term, translations in self.medical_glossary[source_lang].items():
                if ko_term in text and target_lang in translations:
                    text = text.replace(ko_term, translations[target_lang])
                    return f"[Simple Translation] {text}"

        # 원문 반환
        return f"[Translation Failed] {text}"


# 싱글톤 인스턴스
translation_service = TranslationService()
