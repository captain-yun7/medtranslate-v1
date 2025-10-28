"""Anthropic Claude Translation Provider"""

from .base import BaseTranslationProvider
from typing import Optional
import logging
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseTranslationProvider):
    """
    Anthropic Claude를 사용한 번역 프로바이더
    Claude Sonnet, Opus 등 다양한 모델 지원
    """

    def __init__(
        self,
        api_key: str,
        medical_glossary: dict = None,
        model: str = "claude-sonnet-4-5-20250929"
    ):
        """
        Args:
            api_key: Anthropic API 키
            medical_glossary: 의료 용어집
            model: 사용할 Claude 모델
        """
        super().__init__(medical_glossary)
        self.api_key = api_key
        self.model = model
        self.client: Optional[AsyncAnthropic] = None

        # API 키 유효성 확인
        if self.api_key and self.api_key != "your-api-key-here":
            try:
                self.client = AsyncAnthropic(api_key=self.api_key)
                logger.info(f"Claude provider initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.client = None

    @property
    def name(self) -> str:
        return f"Claude-{self.model.split('-')[1]}"  # claude-sonnet -> Sonnet

    def is_available(self) -> bool:
        """Claude API 키가 유효한지 확인"""
        return self.client is not None

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        Claude API로 번역

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어 코드
            target_lang: 타겟 언어 코드
            context: 컨텍스트

        Returns:
            번역된 텍스트
        """
        if not self.is_available():
            raise ValueError("Claude provider is not available (missing API key)")

        # 용어집 컨텍스트
        glossary_context = self._create_glossary_context(source_lang, target_lang)

        # 프롬프트 생성
        prompt = self._create_prompt(
            text, source_lang, target_lang, context, glossary_context
        )

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            translated_text = message.content[0].text.strip()
            logger.info(f"Claude translation completed: {text[:30]}... -> {translated_text[:30]}...")
            return translated_text

        except Exception as e:
            logger.error(f"Claude translation error: {e}")
            raise

    def _create_prompt(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str,
        glossary_context: str
    ) -> str:
        """Claude용 프롬프트 생성"""
        source_name = self._get_lang_name(source_lang)
        target_name = self._get_lang_name(target_lang)

        if context == 'medical':
            prompt = f"""당신은 의료 전문 통역사입니다.
다음 의료 상담 메시지를 {target_name}로 정확하게 번역해주세요.

원문 언어: {source_name}
원문: {text}
"""
            if glossary_context:
                prompt += f"""
의료 용어 참고:
{glossary_context}
"""
            prompt += """
번역 시 주의사항:
1. 의료 용어는 정확하게 번역
2. 환자/의료진의 의도와 감정을 정확히 전달
3. 격식있고 공손한 표현 사용
4. 증상이나 통증 표현은 명확하게 번역
5. 문화적 차이를 고려한 자연스러운 표현

번역문만 출력하세요. 설명이나 주석 없이 번역 결과만 제공하세요."""
        else:
            prompt = f"""다음 텍스트를 {source_name}에서 {target_name}로 번역해주세요.

원문: {text}

번역문만 출력하세요."""

        return prompt
