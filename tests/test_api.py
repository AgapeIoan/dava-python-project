from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    """O dependinta care foloseste baza de date de test."""
    database = None
    try:
        database = TestingSessionLocal()
        yield database
    finally:
        if database:
            database.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_calculate_power_happy_path():
    """Testeaza cazul de succes pentru endpoint-ul /power."""
    response = client.post(
        "/api/v1/power",
        json={"base": 2, "exponent": 8}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 256.0

    db = TestingSessionLocal()
    from app.db.models import ApiRequest
    log_entry = db.query(ApiRequest).first()
    assert log_entry is not None
    assert log_entry.operation_type == "power"
    db.close()

def test_api_power_strips_tiny_imaginary_part():
    """
    Testeaza API-ul pentru a verifica eliminarea partii imaginare foarte mici.
    (2+0j)**2 ar trebui sa returneze "4.0", nu "4.0+0.0j".
    """
    # Arrange: Pregatim payload-ul JSON cu string-uri, asa cum cere noul API
    payload = {"base": "2+0j", "exponent": "2"}

    # Act: Facem cererea POST catre endpoint-ul /power
    response = client.post("/api/v1/power", json=payload)

    # Assert: Verificam raspunsul
    assert response.status_code == 200
    data = response.json()
    # Verificam ca 'result' este un string care poate fi convertit la float
    # si ca valoarea este cea corecta.
    assert float(data["result"]) == 4.0


def test_api_power_with_complex_numbers():
    """
    Testeaza API-ul cu un input si output complex.
    """
    payload = {"base": "-2+5j", "exponent": "2+1j"}

    response = client.post("/api/v1/power", json=payload)

    assert response.status_code == 200
    data = response.json()


    assert "result" in data
    assert "j" in data["result"]
    # Verificam ca incepe aproximativ corect
    assert data["result"].startswith("3.159")
    # Verificam ca partea imaginara este negativa
    assert "-" in data["result"][1:]