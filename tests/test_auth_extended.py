import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker 
from sqlalchemy.pool import StaticPool
from sqlalchemy import delete

from app.db.database import Base, get_db
from app.db.models import User
from app.main import app

import os

TEST_DATABASE_FILE = "test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DATABASE_FILE}"

# Cleanup before running tests
if os.path.exists(TEST_DATABASE_FILE):
    os.remove(TEST_DATABASE_FILE)


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

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_setup_and_teardown():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

client = TestClient(app)

@pytest.mark.asyncio
async def test_signup_and_login():
    # Clean up test user before signup
    from sqlalchemy import delete
    async with AsyncTestingSessionLocal() as session:
        await session.execute(delete(User).where(User.username == "testuser"))
        await session.commit()
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123"
        }
    )
    assert signup_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "StrongPassword123"
        }
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    return login_data["access_token"]

@pytest.mark.asyncio
async def test_invalid_login():
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrong"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"

@pytest.mark.asyncio
async def test_token_auth_and_key_creation():
    token = await test_signup_and_login()
    response = client.post(
        "/apikeys",
        json={"expires_in_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "key" in data

@pytest.mark.asyncio
async def test_token_expiry_simulation():
    # Simulate token that is already expired by manipulating JWT `exp` manually
    from app.core.security import create_access_token
    from datetime import timedelta

    expired_token = create_access_token(data={"sub": "testuser"}, expires_delta=timedelta(seconds=-1))
    response = client.post(
        "/apikeys",
        json={"expires_in_seconds": 3600},
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_revoked_user_cannot_create_api_key():
    token = await test_signup_and_login()

    # Delete user using the same DB session context that FastAPI uses
    async with AsyncTestingSessionLocal() as session:
        await session.execute(delete(User).where(User.username == "testuser"))
        await session.commit()

    # Attempt to use the token after user was deleted
    response = client.post(
        "/apikeys",
        json={"expires_in_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"}
    )

    print(response.json())  # Debugging line to check response
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

