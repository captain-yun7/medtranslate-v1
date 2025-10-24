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
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    # App Settings
    APP_NAME: str = "MedTranslate API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
