from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.core.config import settings
from app.core.security import get_api_key
from app.db.database import engine, Base
from starlette_exporter import PrometheusMiddleware, handle_metrics
from app.core.logging import configure_logging, logger
from app.api.v1.endpoints import math as math_v1, api_key as key_v1, auth as auth_v1, user as user_v1

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: Initializing resources...")

    # DB setup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Startup: Database tables created.")

    # Redis logger (db=1)
    try:
        client = redis_module.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            db=1,
            decode_responses=True
        )
        await client.ping()
        logger.info("✅ Redis logger connection is active.")
        app.core.redis_logger.redis_client = client
        logger.info("🔁 redis_client has been SET globally.")
    except Exception as e:
        logger.error("❌ Redis logger connection failed.", error=str(e))

    yield  # App rulează

    await engine.dispose()
    logger.info("Shutdown: DB closed.")
    if app.core.redis_logger.redis_client:
        await app.core.redis_logger.redis_client.close()
        logger.info("Redis logger connection closed.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Un microserviciu pentru operatii matematice, gata pentru productie.",
    version="1.0.0",
    lifespan=lifespan
)

#for metrics and monitoring
app.add_middleware(PrometheusMiddleware)


app.add_route("/metrics", handle_metrics)

# endpoint test, for checking if the service is running
@app.get("/healthcheck", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Verifica starea de sanatate a serviciului."""
    return {"status": "ok"}


app.include_router(auth_v1.router) #login
app.include_router(key_v1.router) #api keys 
app.include_router(user_v1.router) #delete current user
app.include_router(
    math_v1.router,
    prefix="/api/v1",
    dependencies=[Depends(get_api_key)]
) #mathematical operations

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Bine ai venit la {settings.APP_NAME}!"}
