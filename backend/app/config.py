from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Keys
    ANTHROPIC_API_KEY: str

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
