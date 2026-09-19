from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "GovCareerAI API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    cors_origins: str = ""
    jwt_secret: str = Field(..., validation_alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(60 * 24 * 7, ge=5, le=60 * 24 * 30)
    ingestion_sync_token: str = Field(..., validation_alias="INGESTION_SYNC_TOKEN", min_length=32)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
