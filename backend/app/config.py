"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # App Settings
    app_name: str = "Bo_Check API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bo_check"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 1800  # 30 minutes in seconds
    
    # Scraping
    scrape_delay: float = 2.0  # Delay between requests in seconds
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
