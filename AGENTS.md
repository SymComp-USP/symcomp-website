# AGENTS.md

- Keep changes scoped to the requested area. Do not edit frontend, backend,
  Docker, docs, and legacy code together unless the task requires it.
- `backend/` is the active FastAPI backend. `symcomp-server/` is legacy Django
  reference unless explicitly requested.
- In `frontend/`, use pnpm only; do not create `package-lock.json` or
  `yarn.lock`.
- Do not loosen `frontend/pnpm-workspace.yaml` build-script approvals or
  security overrides without a specific reason.
- Do not use `pnpm test` for frontend verification; it runs `format:fix` and
  modifies files.
- Do not read/commit secrets or `.env` files. Use `.env.example` as the reference.
- After code changes, always run lint and format checks: ESLint for frontend,
  Ruff for backend.
- Commit messages must use Conventional Commits with a scope.
- Commits by agents must include that agent as a `Co-authored-by` trailer.
- Prefer existing patterns and docs before adding new structure.
- Run the narrowest relevant check before handoff and report what ran.
