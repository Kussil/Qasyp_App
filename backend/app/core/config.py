from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://qasyp:qasyp_dev_password@localhost:5432/qasyp"
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "business_profiles"
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ANTHROPIC_API_KEY: str = ""
    EMBEDDING_MODEL_VERSION: str = "multilingual-e5-large"
    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = False
    ALLOWED_ORIGINS: List[str] = []


settings = Settings()
