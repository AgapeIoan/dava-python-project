import pytest
from httpx import AsyncClient
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.core.security import create_access_token
from datetime import timedelta

# Toate importurile de configurare au fost mutate in conftest.py

@pytest.mark.asyncio
async def test_signup_user(client: AsyncClient, db_session: AsyncSession):
    """
    Tests the registration of a new user.

    This test verifies that a new user can sign up and their details are added to the database.

    Args:
        client (AsyncClient): The HTTP client for testing.
        db_session (AsyncSession): The database session instance.

    Asserts:
        - The response status code is 200.
        - The response contains an access token and token type.
        - The user is added to the database with the correct details.
    """
    response = await client.post(
        "/auth/signup",
        json={
            "username": "testsignup",
            "email": "testsignup@example.com",
            "password": "StrongPassword123",
        },
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verificam ca utilizatorul a fost adaugat in baza de date
    result = await db_session.execute(select(User).where(User.username == "testsignup"))
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.email == "testsignup@example.com"

@pytest.mark.asyncio
async def test_signup_duplicate_user(client: AsyncClient, test_user: User):
    """
    Tests that registering a duplicate user fails.

    Args:
        client (AsyncClient): The HTTP client for testing.
        test_user (User): The test user instance.

    Asserts:
        - The response status code is 400.
        - The error detail indicates the username is already registered.
    """
    response = await client.post(
        "/auth/signup",
        json={
            "username": test_user.username, # Folosim user-ul din fixture
            "email": "another@email.com",
            "password": "anotherpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

@pytest.mark.asyncio
async def test_login_for_access_token(client: AsyncClient, test_user: User):
    """
    Tests logging in with valid credentials.

    Args:
        client (AsyncClient): The HTTP client for testing.
        test_user (User): The test user instance.

    Asserts:
        - The response status code is 200.
        - The response contains an access token and token type.
    """
    response = await client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_invalid_login_credentials(client: AsyncClient):
    """
    Tests logging in with invalid credentials.

    Args:
        client (AsyncClient): The HTTP client for testing.

    Asserts:
        - The response status code is 401.
        - The error detail indicates invalid username or password.
    """
    response = await client.post(
        "/auth/login", data={"username": "nonexistent", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"

@pytest.mark.asyncio
async def test_token_auth_for_key_creation(client: AsyncClient, auth_token: str):
    """
    Tests that a valid token can be used to create an API key.

    Args:
        client (AsyncClient): The HTTP client for testing.
        auth_token (str): The JWT token for authentication.

    Asserts:
        - The response status code is 200.
        - The response contains the API key.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post(
        "/apikeys", json={"expires_in_seconds": 3600}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "key" in data

@pytest.mark.asyncio
async def test_expired_token_cannot_create_key(client: AsyncClient):
    """
    Tests that an expired token cannot access protected resources.

    Args:
        client (AsyncClient): The HTTP client for testing.

    Asserts:
        - The response status code is 401.
        - The error detail indicates invalid credentials.
    """
    expired_token = create_access_token(
        data={"sub": "testuser"}, expires_delta=timedelta(seconds=-1)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await client.post(
        "/apikeys", json={"expires_in_seconds": 3600}, headers=headers
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

@pytest.mark.asyncio
async def test_revoked_user_token_is_invalid(client: AsyncClient, db_session: AsyncSession):
    """
    Tests that a token for a deleted user is invalid.

    This test verifies that a token becomes invalid if the associated user is deleted from the database.

    Args:
        client (AsyncClient): The HTTP client for testing.
        db_session (AsyncSession): The database session instance.

    Asserts:
        - The response status code is 401.
        - The error detail indicates invalid credentials.
    """
    # Pas 1: Cream si ne logam cu un utilizator pentru a obtine un token valid
    signup_response = await client.post(
        "/auth/signup",
        json={"username": "tobe_deleted", "email": "deleted@example.com", "password": "a_password"}
    )
    assert signup_response.status_code == 200
    
    login_response = await client.post(
        "/auth/login",
        data={"username": "tobe_deleted", "password": "a_password"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Pas 2: Stergem utilizatorul din baza de date
    await db_session.execute(delete(User).where(User.username == "tobe_deleted"))
    await db_session.commit()

    # Pas 3: Incercam sa folosim token-ul vechi
    response = await client.post(
        "/apikeys", json={"expires_in_seconds": 3600}, headers=headers
    )
    
    # get_current_user va esua pentru ca nu mai gaseste user-ul in BD
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"
