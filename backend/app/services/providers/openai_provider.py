"""OpenAI Translation Provider"""

from .base import BaseTranslationProvider
from typing import Optional
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseTranslationProvider):
    """
    OpenAI GPT를 사용한 번역 프로바이더
    GPT-4, GPT-3.5-turbo 등 다양한 모델 지원
    """

    def __init__(
        self,
        api_key: str,
        medical_glossary: dict = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3
    ):
        """
        Args:
            api_key: OpenAI API 키
            medical_glossary: 의료 용어집
            model: 사용할 모델 (gpt-4, gpt-3.5-turbo 등)
            temperature: 온도 (0.0-1.0, 낮을수록 일관된 번역)
        """
        super().__init__(medical_glossary)
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client: Optional[AsyncOpenAI] = None

        # API 키 유효성 확인
        if self.api_key and self.api_key != "your-api-key-here":
            try:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info(f"OpenAI provider initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    @property
    def name(self) -> str:
        return f"OpenAI-{self.model}"

    def is_available(self) -> bool:
        """OpenAI API 키가 유효한지 확인"""
        return self.client is not None

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: str = 'medical'
    ) -> str:
        """
        OpenAI GPT로 번역

        Args:
            text: 번역할 텍스트
            source_lang: 소스 언어 코드
            target_lang: 타겟 언어 코드
            context: 컨텍스트 (medical, general 등)

        Returns:
            번역된 텍스트
        """
        if not self.is_available():
            raise ValueError("OpenAI provider is not available (missing API key)")

        # 용어집 컨텍스트
        glossary_context = self._create_glossary_context(source_lang, target_lang)

        # 시스템 프롬프트
        system_prompt = self._create_system_prompt(context, glossary_context)

        # 사용자 프롬프트
        user_prompt = self._create_user_prompt(
            text, source_lang, target_lang
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1024
            )

            translated_text = response.choices[0].message.content.strip()
            logger.info(f"OpenAI translation completed: {text[:30]}... -> {translated_text[:30]}...")
            return translated_text

        except Exception as e:
            logger.error(f"OpenAI translation error: {e}")
            raise

    def _create_system_prompt(self, context: str, glossary_context: str) -> str:
        """시스템 프롬프트 생성"""
        if context == 'medical':
            prompt = """You are a professional medical interpreter specialized in healthcare communication.

Your responsibilities:
1. Translate medical consultations accurately and precisely
2. Use correct medical terminology
3. Maintain the tone and intent of the original message
4. Use formal and polite language appropriate for medical settings
5. Clearly convey symptoms, pain, and medical conditions
6. Consider cultural differences in medical communication

Important guidelines:
- Translate ONLY the given text, without adding explanations or commentary
- Preserve the emotional tone and urgency when relevant
- Use standardized medical terminology when available
- Be sensitive to patient concerns and cultural nuances"""

            if glossary_context:
                prompt += f"\n\nMedical Terminology Reference:\n{glossary_context}"

            return prompt
        else:
            return "You are a professional translator. Translate the text accurately while maintaining the original tone and intent."

    def _create_user_prompt(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """사용자 프롬프트 생성"""
        source_name = self._get_lang_name(source_lang)
        target_name = self._get_lang_name(target_lang)

        return f"""Translate the following text from {source_name} to {target_name}.

Source text ({source_name}):
{text}

Provide ONLY the translation in {target_name}, without any explanations or additional text."""
