# Backend

Backend for Symcomp's Website.

Project stack: FastAPI, SQLAlchemy ORM + Alembic, PostgreSQL with async driver,
Ruff for linting & formatting, Pytest for testing

## Getting started

This project uses `uv` for management. We'll assume `uv` is used for every dev, but you might
try to work with `pip` if that's what you prefer.

To install `uv`, use:

```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, create a *venv*:

```bash 
$ uv venv
```

Lastly, use `uv sync` to install dependencies on virtual environment.

## ORM and Alembic workflow

When using SQLAlchemy ORM paired with Alembic for migrations, workflow is mostly:

1. Chande or add an SQLAlchemy. Example:

```python 
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    price: Mapped[float]
```

2. Generate a migration:

```bash
$ uv run alembic revision --autogenerate -m "<message describing change"
```

3. Review the generated migration.

Check for table names, fields, defaults, foreign keys, etc. Add data changes manually if needed.

4. Apply locally:

```bash
$ uv run alembic upgrade head
```

5. Commit your changes. 

Commit together: SQLAlchemy model changes, migration files (under `alembic/versions/`) and tests for new behaviour. In new environments, `alembic upgrade head` builds the full schema from zero.

### Login social (Google e GitHub)

Defina no ambiente do backend `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `OAUTH_REDIRECT_BASE` (origem pública
que encaminha `/api` ao backend) e `FRONTEND_BASE_URL`. Cadastre nos consoles OAuth
as callbacks `/api/v1/auth/oauth/google/callback` e
`/api/v1/auth/oauth/github/callback` sob essa origem. Execute `alembic upgrade head`
para adicionar `users.oauth_provider`. O login exige e-mail verificado; e-mails já
associados a contas com senha não são vinculados automaticamente.
