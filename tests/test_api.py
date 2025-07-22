
import pytest
import pytest_asyncio  # <--- PASUL 1: Importam pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.models import ApiRequest
from app.main import app
from app.core.config import settings

# Configurarea bazei de date ramane la fel
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# PASUL 2: Schimbam decoratorul fixture-ului
@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_setup_and_teardown():
    """
    Acest fixture ruleaza automat pentru fiecare functie de test.
    - Creeaza toate tabelele inainte de test.
    - Sterge toate tabelele dupa ce testul s-a terminat.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


client = TestClient(app)


# Testele raman la fel, marcate cu @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_calculate_power_happy_path():
    response = client.post("/apikeys", json={"expires_in_seconds": 60})
    assert response.status_code == 200
    data = response.json()
    assert "key" in data and "expires_at" in data
    new_key = data["key"]

    # Step 2: use the generated key for the power endpoint
    headers = {settings.API_KEY_NAME: new_key}
    response = client.post(
        "/api/v1/power",
        json={"base": "2", "exponent": "8"},
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert str(data["result"]) == "256.0"

    async with AsyncTestingSessionLocal() as session:
        result = await session.execute(select(ApiRequest))
        log_entry = result.scalar_one_or_none()

    assert log_entry is not None
    assert log_entry.operation_type == "power"


@pytest.mark.asyncio
async def test_api_power_strips_tiny_imaginary_part():
    response = client.post("/apikeys", json={"expires_in_seconds": 60})
    assert response.status_code == 200
    data = response.json()
    assert "key" in data and "expires_at" in data
    new_key = data["key"]

    # Step 2: use the generated key for the power endpoint
    headers = {settings.API_KEY_NAME: new_key}
    payload = {"base": "2+0j", "exponent": "2"}
    response = client.post("/api/v1/power", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert str(data["result"]) == "4.0"


@pytest.mark.asyncio
async def test_api_power_with_complex_numbers():
    response = client.post("/apikeys", json={"expires_in_seconds": 60})
    assert response.status_code == 200
    data = response.json()
    assert "key" in data and "expires_at" in data
    new_key = data["key"]

    # Step 2: use the generated key for the power endpoint
    headers = {settings.API_KEY_NAME: new_key}
    payload = {"base": "-2+5j", "exponent": "2+1j"}
    print(settings.API_KEY)
    response = client.post("/api/v1/power", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "j" in data["result"]

@pytest.mark.asyncio
async def test_api_power_missing_api_key():
    # Attempt to call the endpoint without any API key header
    response = client.post(
        "/api/v1/power",
        json={"base": "2", "exponent": "3"}
    )
    # Expect Unauthorized
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid or missing API Key"

@pytest.mark.asyncio
async def test_generate_and_use_api_key():
    # Step 1: generate a new API key
    response = client.post("/apikeys", json={"expires_in_seconds": 60})
    assert response.status_code == 200
    data = response.json()
    assert "key" in data and "expires_at" in data
    new_key = data["key"]

    # Step 2: use the generated key for the power endpoint
    headers = {settings.API_KEY_NAME: new_key}
    response2 = client.post(
        "/api/v1/power",
        json={"base": "3", "exponent": "2"},
        headers=headers
    )
    assert response2.status_code == 200
    assert str(response2.json()["result"]) == "9.0"