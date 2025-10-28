"""Base Translation Provider Interface"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTranslationProvider(ABC):
    """
    추상 번역 프로바이더 베이스 클래스
    모든 번역 프로바이더는 이 클래스를 상속받아 구현해야 합니다.
    """

    def __init__(self, medical_glossary: Dict = None):
        """
        Args:
            medical_glossary: 의료 용어집 딕셔너리
        """
        self.medical_glossary = medical_glossary or {}
        self.lang_names = {
            'ko': '한국어',
            'en': 'English',
            'ja': '日本語',
            'zh': '中文',
            'vi': 'Tiếng Việt',
            'th': 'ภาษาไทย'
        }

    @abstractmethod
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        텍스트를 번역합니다.

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어 코드 (예: 'vi', 'en')
            target_lang: 타겟 언어 코드 (예: 'ko', 'en')
            context: 번역 컨텍스트 (예: 'medical', 'general')

        Returns:
            번역된 텍스트
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        프로바이더가 사용 가능한지 확인합니다.
        (예: API 키가 설정되어 있는지)

        Returns:
            사용 가능 여부
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """프로바이더 이름"""
        pass

    def _create_glossary_context(self, source_lang: str, target_lang: str) -> str:
        """
        용어집 컨텍스트 생성 (모든 프로바이더 공통)

        Args:
            source_lang: 소스 언어
            target_lang: 타겟 언어

        Returns:
            용어집 컨텍스트 문자열
        """
        if 'ko' not in self.medical_glossary:
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

    def _get_lang_name(self, lang_code: str) -> str:
        """언어 코드를 언어명으로 변환"""
        return self.lang_names.get(lang_code, lang_code)
