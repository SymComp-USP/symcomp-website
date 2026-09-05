from enum import StrEnum
from functools import lru_cache
from typing import TypeAlias

from pydantic import AnyHttpUrl, Field, HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    development = "dev"
    production = "prod"


CorsOrigin: TypeAlias = HttpUrl | AnyHttpUrl


class Settings(BaseSettings):
    app_env: AppEnv = Field(
        default=AppEnv.development,
        title="App environment",
        description="Whether the app is in production or in development",
    )

    database_url: PostgresDsn = Field(
        default_factory=lambda: PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            path="symcomp",
        ),
        title="Database URL",
        description="The database connection string",
    )

    cors_origins: set[CorsOrigin] = Field(
        default_factory=set[CorsOrigin],
        title="Cross-Origin Resource Sharing origins",
        description="HTTP url's recognized by the server",
    )

    secret_key: str = Field(
        title="Secret Key",
        description="Chave secreta para assinatura de tokens/sessões",
    )

    model_config = SettingsConfigDict(
        env_file=".env", validate_default=True, case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
