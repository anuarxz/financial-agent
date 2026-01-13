"""Application settings and configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_host: str = "localhost"
    database_port: int = 5433
    database_name: str = "financial_agent"
    database_user: str = "postgres"
    database_password: str = "postgres"

    model_name: str = "gemini/gemini-2.5-flash"

    reasoning_effort: str = "low"

    max_iterations: int = 10

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 


@lru_cache
def get_settings() -> Settings:
    return Settings()
