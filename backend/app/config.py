from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Translation Provider Settings
    TRANSLATION_PROVIDER: str = "mock"  # 'openai', 'claude', 'mock'

    # API Keys
    ANTHROPIC_API_KEY: str = "your-api-key-here"
    OPENAI_API_KEY: str = "your-api-key-here"

    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-3.5-turbo"  # 'gpt-4', 'gpt-3.5-turbo'
    OPENAI_TEMPERATURE: float = 0.3

    # Claude Settings
    CLAUDE_MODEL: str = "claude-sonnet-4-5-20250929"

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/medtranslate"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # CORS
    CORS_ORIGINS: List[str] = [
        "https://chat.medtranslate.co.kr",
        "https://admin.medtranslate.co.kr",
        # 테스트용 포트 범위 (3000-3009)
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "http://localhost:3007",
        "http://localhost:3008",
        "http://localhost:3009",
    ]

    # App Settings
    APP_NAME: str = "MedTranslate API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # JWT Settings
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
