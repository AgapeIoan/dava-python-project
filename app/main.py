from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine, Base
from app.api.v1.endpoints import math as math_v1

# Creeaza tabelele in baza de date (daca nu exista) la pornirea aplicatiei
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Un microserviciu pentru operatii matematice, gata pentru productie.",
    version="1.0.0"
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