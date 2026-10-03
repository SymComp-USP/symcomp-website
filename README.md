# SymComp

Next.js frontend (`frontend/`), FastAPI backend (`backend/`), and PostgreSQL.
`symcomp-server/` is archived Django reference code.

## Local development

```bash
docker compose -f docker-compose.dev.yml up --build
```

Open http://localhost:3000. API documentation is at http://localhost:8000/docs.
Development uses its own Compose project and database volume; it requires no
`.env` file. Existing volumes from the old default development stack are not
migrated automatically.

Seed the local Semana event and an input challenge:

```bash
docker compose -f docker-compose.dev.yml exec backend python -m scripts.seed_dev
```

```bash
docker compose -f docker-compose.dev.yml exec backend ruff check .
docker compose -f docker-compose.dev.yml exec backend ruff format --check .
docker compose -f docker-compose.dev.yml exec backend pytest
docker compose -f docker-compose.dev.yml exec frontend pnpm run lint
docker compose -f docker-compose.dev.yml exec frontend pnpm run format
```

Backend tests use the development database; use a disposable local database for
integration tests. CI provides a separate PostgreSQL service. Do not run tests
against production. `pnpm test` modifies formatting; use the explicit checks above.

## Production

The default Compose file runs Caddy, Next.js, FastAPI, and PostgreSQL on one VM.
Follow [the deployment guide](docs/deployment.md) to configure DNS, credentials,
backups, and the firewall before running:

```bash
docker compose up -d --build
```

To fill up the initial semana data (after confirming it right):

```bash
docker compose exec backend python -m scripts.seed_semana_data
```