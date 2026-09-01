from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import config, database
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
