"""Mock Translation Provider for Testing"""

from .base import BaseTranslationProvider
import logging

logger = logging.getLogger(__name__)


class MockProvider(BaseTranslationProvider):
    """
    테스트용 Mock 번역 프로바이더
    실제 번역 대신 포맷된 문자열을 반환합니다.
    """

    def __init__(self, medical_glossary: dict = None):
        """
        Args:
            medical_glossary: 의료 용어집 (간단한 용어 대체에 사용)
        """
        super().__init__(medical_glossary)
        logger.info("Mock provider initialized")

    @property
    def name(self) -> str:
        return "Mock"

    def is_available(self) -> bool:
        """Mock은 항상 사용 가능"""
        return True

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        Mock 번역 수행

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어 코드
            target_lang: 타겟 언어 코드
            context: 컨텍스트

        Returns:
            포맷된 Mock 번역 텍스트
        """
        # 간단한 용어집 기반 번역 시도
        translated = self._simple_glossary_translation(text, source_lang, target_lang)

        if translated != text:
            # 용어집에서 번역을 찾은 경우
            logger.info(f"Mock translation (glossary): {text} -> {translated}")
            return translated

        # 용어집에 없는 경우 Mock 표시
        source_name = self._get_lang_name(source_lang)
        target_name = self._get_lang_name(target_lang)

        mock_translation = f"[MOCK] {text} (translated from {source_name} to {target_name})"
        logger.info(f"Mock translation: {text[:30]}... -> {mock_translation[:30]}...")

        return mock_translation

    def _simple_glossary_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        간단한 용어집 기반 번역 (완전 일치만)

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어
            target_lang: 타겟 언어

        Returns:
            번역된 텍스트 (또는 원문)
        """
        if 'ko' not in self.medical_glossary:
            return text

        # 한국어 -> 다른 언어
        if source_lang == 'ko':
            for ko_term, translations in self.medical_glossary['ko'].items():
                if ko_term == text.strip() and target_lang in translations:
                    return translations[target_lang]

        # 다른 언어 -> 한국어
        elif target_lang == 'ko':
            for ko_term, translations in self.medical_glossary['ko'].items():
                if source_lang in translations:
                    source_term = translations[source_lang]
                    if source_term == text.strip():
                        return ko_term

        return text
