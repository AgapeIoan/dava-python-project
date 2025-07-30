import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.models import ApiRequest
from app.main import app
from app.core.config import settings

# Use in-memory SQLite database for testing
import os

TEST_DATABASE_FILE = "test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DATABASE_FILE}"

# Cleanup before running tests
if os.path.exists(TEST_DATABASE_FILE):
    os.remove(TEST_DATABASE_FILE)


# Create async engine and session factory
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Override dependency to use test DB session
async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Automatically setup and teardown DB for each test
@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Test client
client = TestClient(app)

def get_auth_headers():
    """Helper function to sign up or log in and return valid auth headers."""
    signup_response = client.post(
        "/auth/signup",
        json={"username": "testuser", "email": "test@example.com", "password": "StrongPassword123"}
    )

    if signup_response.status_code != 200:
        login_response = client.post(
            "/auth/login",
            json={"username": "testuser", "password": "StrongPassword123"}
        )
        token = login_response.json()["access_token"]
    else:
        token = signup_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_calculate_power_happy_path(db_setup_and_teardown):
    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    assert response.status_code == 200
    api_key = response.json()["key"]

    headers[settings.API_KEY_NAME] = api_key
    response = client.post("/api/v1/power", json={"base": "2", "exponent": "8"}, headers=headers)
    assert response.status_code == 200
    assert str(response.json()["result"]) == "256.0"

    async with AsyncTestingSessionLocal() as session:
        result = await session.execute(select(ApiRequest))
        log_entry = result.scalar_one_or_none()
    assert log_entry is not None
    assert log_entry.operation_type == "power"

@pytest.mark.asyncio
async def test_api_power_strips_tiny_imaginary_part(db_setup_and_teardown):
    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    api_key = response.json()["key"]
    headers[settings.API_KEY_NAME] = api_key
    payload = {"base": "2+0j", "exponent": "2"}
    response = client.post("/api/v1/power", json=payload, headers=headers)
    assert response.status_code == 200
    assert str(response.json()["result"]) == "4.0"
  
@pytest.mark.asyncio
async def test_api_power_with_complex_numbers(db_setup_and_teardown):
    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    api_key = response.json()["key"]
    headers[settings.API_KEY_NAME] = api_key
    payload = {"base": "-2+5j", "exponent": "2+1j"}
    response = client.post("/api/v1/power", json=payload, headers=headers)
    assert response.status_code == 200
    assert "j" in response.json()["result"]

@pytest.mark.asyncio
async def test_api_power_missing_api_key():
    response = client.post("/api/v1/power", json={"base": "2", "exponent": "3"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

@pytest.mark.asyncio
async def test_generate_and_use_api_key(db_setup_and_teardown):
    headers = get_auth_headers()
    response = client.post("/apikeys", json={"expires_in_seconds": 60}, headers=headers)
    api_key = response.json()["key"]

    headers[settings.API_KEY_NAME] = api_key
    response2 = client.post("/api/v1/power", json={"base": "3", "exponent": "2"}, headers=headers)
    assert response2.status_code == 200
    assert str(response2.json()["result"]) == "9.0"
