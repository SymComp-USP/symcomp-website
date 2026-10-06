import secrets
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
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

    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    github_client_id: str | None = None
    github_client_secret: SecretStr | None = None
    oauth_redirect_base: AnyHttpUrl = Field(default="http://localhost:8000")
    frontend_base_url: AnyHttpUrl = Field(default="http://localhost:3000")

    media_root: Path = Field(
        # o default aqui assume /backend/app/core/config.py como caminho deste arquivo
        # se isso mudar, é bom atualizar
        default=Path(__file__).resolve().parents[2] / "media",
        title="Media directory relative path",
        description="Caminho relativo para armazenamento de imagens, como as capas dos Challenges, no servidor",
    )

    media_url_prefix: str = Field(default="/media", title="Media directory path prefix")

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from: str | None = None
    smtp_use_tls: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
