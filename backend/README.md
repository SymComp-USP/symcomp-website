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

## Contributing 

For commits, use **Conventional Commits**. Format:

```
<type>(<scope>): <description>

[body, optional]
```

Example:

- `feat(auth): add google oauth2 login integration`

Check Conventional Commits [docs](www.conventionalcommits.org/en/v1.0.0/)

To make PRs, follow these guidelines:
- Keep it focused: One PR should address one issue or feature, unless absolutely necessary.
- Write tests: Ensure new code has matching tests.
- Run linters: Run lint, format and tests locally before pushing.
- Use our PR template.

For branches, use specific prefixes to indentify their purpose. Examples:

- `feat/short-description`
- `docs/some-message`

This is a recommendation, but may be ignored if needed.

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
