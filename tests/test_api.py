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
    assert '"base": 2.0' in log_entry.input_params
    db.close()