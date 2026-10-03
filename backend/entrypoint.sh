#!/bin/sh
set -e

if [ "$APP_ENV" = "dev" ] && command -v uv >/dev/null 2>&1; then
    uv sync --frozen --link-mode=copy
fi

alembic upgrade head
exec "$@"
