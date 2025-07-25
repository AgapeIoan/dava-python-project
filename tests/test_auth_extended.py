import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_signup_and_login():
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123"
        }
    )
    assert signup_response.status_code == 200
    token = signup_response.json()["access_token"]

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

    # Simulate user deletion from DB directly
    from app.db.database import get_db
    from app.db.models import User
    from sqlalchemy import delete

    async for db in get_db():
        await db.execute(delete(User).where(User.username == "testuser"))
        await db.commit()
        break

    response = client.post(
        "/apikeys",
        json={"expires_in_seconds": 3600},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
