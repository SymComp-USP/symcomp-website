#!/usr/bin/env python3

"""
Promove um usuário a admin. Opcionalmente cria o usuário se ele não existir.

Uso:
    # Promove usuário existente
    uv run python -m scripts.promote_admin admin@exemplo.com

    # Cria primeiro admin em banco novo
    uv run python -m scripts.promote_admin admin@exemplo.com \
        --create --name "admin"

    # Sem --password, o script pede a senha interativamente (não aparece
    # no histórico do shell nem em `ps aux`).

Idempotente: rodar várias vezes não quebra nem duplica.
"""

import argparse
import asyncio
import getpass
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password
from app.core.config import get_settings
from app.core.database import create_database
from app.users.models import User

# ---------------------------------------------------------------------------
# Infraestrutura do script
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _session_scope() -> AsyncIterator[AsyncSession]:
    """Sessão standalone para CLI, com commit/rollback automáticos.

    Não usa `get_session` do FastAPI (que depende de `request.app.state`).
    """
    settings = get_settings()
    engine, session_factory = create_database(settings)

    try:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        await engine.dispose()


# ---------------------------------------------------------------------------
# Operações
# ---------------------------------------------------------------------------


async def _get_by_email(session: AsyncSession, email: str) -> User | None:
    return await session.scalar(select(User).where(User.email == email))


async def _promote(session: AsyncSession, user: User) -> None:
    user.is_admin = True
    user.is_verified = True
    user.deleted_at = None  # reativa se estava soft-deleted
    await session.flush()


async def _create(session: AsyncSession, email: str, name: str, password: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        is_admin=True,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    return user


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_password(args: argparse.Namespace) -> str:
    if args.password:
        return args.password
    if env := os.environ.get("ADMIN_PASSWORD"):
        return env
    return getpass.getpass("Senha do admin: ")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email", help="Email do admin.")
    parser.add_argument(
        "--create",
        action="store_true",
        help="Cria o usuário se não existir.",
    )
    parser.add_argument("--name", help="Nome (obrigatório com --create).")
    parser.add_argument(
        "--password",
        help="Senha. Se ausente, usa $ADMIN_PASSWORD ou pede interativamente.",
    )
    args = parser.parse_args()

    async with _session_scope() as session:
        user = await _get_by_email(session, args.email)

        if user is not None:
            await _promote(session, user)
            print(f"✓ {args.email} promovido a admin.")
            return 0

        if not args.create:
            print(
                f"✗ Usuário {args.email!r} não existe. Use --create para criá-lo.",
                file=sys.stderr,
            )
            return 1

        if not args.name:
            print(
                "✗ --name é obrigatório com --create.",
                file=sys.stderr,
            )
            return 1

        password = _resolve_password(args)
        if not password:
            print("✗ Senha vazia.", file=sys.stderr)
            return 1

        await _create(session, args.email, args.name, password)
        print(f"✓ Admin {args.email} criado.")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
