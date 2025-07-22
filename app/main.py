from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.security import get_api_key
from app.db.database import engine, Base
from starlette_exporter import PrometheusMiddleware, handle_metrics
from app.core.logging import configure_logging, logger
from app.api.v1.endpoints import math as math_v1, api_key as key_v1

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    """
    logger.info("Startup: Initializing resources...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Startup: Database tables created.")

    yield  # Aplicatia ruleaza intre startup si shutdown

    logger.info("Shutdown: Closing resources...")
    await engine.dispose()
    logger.info("Shutdown: Resources closed.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Un microserviciu pentru operatii matematice, gata pentru productie.",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware pentru Prometheus
app.add_middleware(PrometheusMiddleware)

# Endpointul /metrics
app.add_route("/metrics", handle_metrics)

# Endpoint de test, pentru a verifica daca serviciul este pornit si functional
@app.get("/healthcheck", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Verifica starea de sanatate a serviciului."""
    return {"status": "ok"}

# Includem rutele definite in alt fisier. Momentan, math.py este gol.
app.include_router(key_v1.router)
app.include_router(
    math_v1.router,
    prefix="/api/v1",
    dependencies=[Depends(get_api_key)]
)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Bine ai venit la {settings.APP_NAME}!"}
