from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "HR API"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    cors_origins: list[str] = ["http://localhost:5173"]  # JSON list in .env


@lru_cache
def get_settings() -> Settings:
    """Build Settings once; every later call returns the same object."""
    return Settings()
