import secrets
from enum import StrEnum
from functools import lru_cache
from typing import TypeAlias

from pydantic import AnyHttpUrl, Field, HttpUrl, PostgresDsn, SecretStr
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

    # Lembre-se de ler como settings.secret_key.get_secret_value()
    secret_key: SecretStr = Field(
        default_factory=lambda: SecretStr(secrets.token_urlsafe(32)),
        title="Secret Key",
        description="Chave secreta para assinatura de tokens/sessões",
    )

    token_algorithm: str = Field(
        default="HS256",
        title="Token Algorithm",
        description="Algoritmo de criptografia utilizado para assinar os tokens JWT",
    )

    access_token_expire_minutes: int = Field(
        default=15,
        title="Access Token Expire Time (minutes)",
        description="Tempo (em minutos) de validade de um token de acesso JWT",
    )

    refresh_token_expire_days: int = Field(
        default=7,
        title="Refresh Token Expire Time (days)",
        description="Tempo (em dias) de validade de um token de revalidação de acesso",
    )

    model_config = SettingsConfigDict(
        env_file=".env", validate_default=True, case_sensitive=False
    )

    issuer: AnyHttpUrl = Field(
        default="http://localhost:8000",
        title="Issuer",
        description="URL que identifica este servidor (claim 'iss' do id_token)",
    )

    audience: str = Field(
        default="symcomp-frontend",
        title="Audience (client_id)",
        description="Identificador do cliente que consome o id_token (claim 'aud')",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
