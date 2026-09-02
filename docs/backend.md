# Backend reference

The new FastAPI service is in `backend/`; the archived Django implementation is
in `symcomp-server/`.

## Layout

```text
app/
  api/           # routers and dependencies
  core/          # settings, database, security
  models/        # SQLAlchemy models
  repositories/  # database access
  schemas/       # Pydantic request/response models
  services/      # business rules
```

Use `/api/v1` for the new API. Keep routers thin: routes call services, and
services use repositories.

## Legacy endpoints to review

| Legacy endpoint | Purpose | Keep? |
| --- | --- | --- |
| `POST /api/register/` | Register a user and send a verification code | Yes |
| `POST /api/token/` | Login; legacy sets JWT cookies | Yes |
| `POST /api/token/refresh/` | Refresh access token | Yes |
| `POST /api/validate-code/` | Verify email | Yes |
| `GET /api/me/` | Current user, role, and challenge player | Yes |
| `POST /api/promover/` | Change a user's role | Review |
| `GET, POST /api/palestrante/` | List/create speakers | Review |
| `GET /desafio/listar/` | List challenges | Yes |
| `POST /desafio/{id}/join/` | Join a challenge | Yes |
| `GET /desafio/{id}/questoes/` | List questions and saved answers | Yes |
| `POST /desafio/respostas/salvar/` | Save one answer | Optional |
| `POST /desafio/{id}/respostas/salvar-em-lote/` | Save answers | Yes |
| `POST /desafio/{id}/submeter/` | Submit and score a challenge | Yes |
| `GET /desafio/{id}/ranking/` | Public ranking | Yes |
| `POST /api/atividades/registrar-presenca/` | Register QR attendance | Yes |
| `POST /email/send-verification/` | Legacy HTML email form | No; replace with API flow |

The legacy API uses `/api` and `/desafio`; the frontend must be updated to the
new versioned paths rather than preserving these prefixes by default.

## Models/data to check

| New model | Legacy source | Notes |
| --- | --- | --- |
| `User` | `api.User` | Email, name, password hash, verified/active state |
| `Role` / `UserRole` | `PerfilUsuario`, user role flags | Use a mapping table; legacy roles are participant, speaker, organizer, president |
| `EmailVerificationToken` | `EmailVerificationCode` | Create new expiring, hashed tokens; do not copy old codes |
| `Speaker`, `SpeakerLink` | `Palestrante`, `Link` | Import only if the content is still current |
| `Challenge`, `Question` | `Desafio`, `Questao` | Preserve title, question, answer, and points as needed |
| `ChallengeParticipant` | `Jogador`, `Daname` | Allow a user in multiple challenges; nickname pool is optional |
| `Answer` | `Resposta` | One answer per participant/question |
| `Activity`, `Attendance` | `Atividade`, `Presenca` | Preserve schedule, attendance, and email-consent data if needed |
| `ActivityPoints` | `AtividadePontos` | Optional activity reward configuration |

Prefer a password reset for imported accounts;

## Model Conventions

- Use UUID rather than integer IDs for primary keys.
- Table names match model names, but using lowercase and plural. For example: Model "User" -> table "users".
- Every instanced model is automatically filled with "created_at", "updated_at" and "deleted_at"* fields.
- Foreign keys are indexed automatically. Constraint names are standardized via SQLAlchemy's MetaData conventions. You should also index frequently searched fields.

These conventions are coded in the base model class, at backend/app/models/base.py.

\* Data is never physically deleted: we use the "deleted_at" field to control if a record is meant to be deleted (i.e. "soft delete").

## Important rules

- PostgreSQL remains the database; create a new schema with Alembic rather
  than reusing Django tables.
- Keep secrets in environment variables. Use explicit CORS origins and secure
  HttpOnly cookies if retaining cookie authentication.
