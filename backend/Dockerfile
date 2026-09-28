# ==========================================
# 1. BASE STAGE
# ==========================================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ==========================================
# 2. BUILDER STAGE
# ==========================================
FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# ==========================================
# 3. RUNTIME STAGE
# ==========================================
FROM base AS runtime

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8000

# ==========================================
# 4. DEVELOPMENT STAGE
# ==========================================
FROM runtime AS development

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

RUN uv sync --frozen

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==========================================
# 5. PRODUCTION STAGE
# ==========================================
FROM runtime AS production

RUN addgroup --system app && adduser --system --group app

RUN chown -R app:app /app

USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]