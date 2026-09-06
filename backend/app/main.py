from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import config, database
from app.core.exceptions.app_errors import AppError
from app.core.exceptions.handlers import app_error_handler, exception_handler
from app.core.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = config.get_settings()
    engine, session_factory = database.create_database(settings)

    app.state.engine = engine
    app.state.session_factory = session_factory

    yield
    await engine.dispose()


app = FastAPI(title="SymComp API", version="0.1.0", lifespan=lifespan)
app.include_router(health_router, prefix="/api/v1")

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, exception_handler)
