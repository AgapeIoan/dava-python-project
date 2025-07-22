from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine, Base
from app.api.v1.endpoints import math as math_v1

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    """
    print("Startup: Initializing resources...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional
        await conn.run_sync(Base.metadata.create_all)
    print("Startup: Database tables created.")

    yield  # Aplicatia ruleaza intre startup si shutdown

    print("Shutdown: Closing resources...")
    await engine.dispose()
    print("Shutdown: Resources closed.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Un microserviciu pentru operatii matematice, gata pentru productie.",
    version="1.0.0",
    lifespan=lifespan
)

# Endpoint de test, pentru a verifica daca serviciul este pornit si functional
@app.get("/healthcheck", tags=["Monitoring"])
def health_check() -> dict[str, str]:
    """Verifica starea de sanatate a serviciului."""
    return {"status": "ok"}

# Includem rutele definite in alt fisier. Momentan, math.py este gol.
app.include_router(math_v1.router, prefix="/api/v1")

@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"Bine ai venit la {settings.APP_NAME}!"}