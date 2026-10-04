from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.atividade.routes import admin_router as atividade_admin_router
from app.atividade.routes import attendance_router as atividade_attendance_router
from app.atividade.routes import router as atividade_router
from app.auth.oauth.routes import router as oauth_router
from app.auth.routes import router as auth_router
from app.challenges.admin_routes import router as challenge_admin_router
from app.challenges.routes import router as challenge_router
from app.core import config, database
from app.core.exceptions.app_errors import AppError
from app.core.exceptions.handlers import app_error_handler, exception_handler
from app.core.health import router as health_router
from app.core.rate_limit import RateLimitMiddleware
from app.semana.routes import admin_router as semana_admin_router
from app.semana.routes import router as semana_router
from app.users.admin_router import router as user_admin_router
from app.users.routes import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = config.get_settings()
    settings.media_root.mkdir(parents=True, exist_ok=True)
    engine, session_factory = database.create_database(settings)

    app.state.engine = engine
    app.state.session_factory = session_factory

    yield
    await engine.dispose()


app = FastAPI(title="SymComp API", version="0.1.0", lifespan=lifespan)
_settings = config.get_settings()

if _settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in _settings.cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(RateLimitMiddleware)

# ---------------------------------------------------------------------------
# Rotas da API
# ---------------------------------------------------------------------------

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(oauth_router, prefix="/api/v1/auth")
app.include_router(user_router, prefix="/api/v1/user")
app.include_router(semana_router, prefix="/api/v1")
app.include_router(semana_admin_router, prefix="/api/v1")
app.include_router(atividade_router, prefix="/api/v1")
app.include_router(atividade_admin_router, prefix="/api/v1")
app.include_router(atividade_attendance_router, prefix="/api/v1")
app.include_router(user_admin_router, prefix="/api/v1/admin/users")
app.include_router(challenge_router, prefix="/api/v1/challenge")
app.include_router(challenge_admin_router, prefix="/api/v1/admin/challenge")

# ---------------------------------------------------------------------------
# Arquivos estáticos (imagens de challenges)
# ---------------------------------------------------------------------------

app.mount(
    _settings.media_url_prefix,
    StaticFiles(directory=_settings.media_root, check_dir=False),
    name="media",
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, exception_handler)
