# tests/test_auth_extended.py

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
    """Testeaza inregistrarea unui utilizator nou."""
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
    """Testeaza ca inregistrarea unui utilizator duplicat esueaza."""
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
    """Testeaza logarea cu credentiale valide."""
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
    """Testeaza logarea cu credentiale invalide."""
    response = await client.post(
        "/auth/login", data={"username": "nonexistent", "password": "wrong"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"

@pytest.mark.asyncio
async def test_token_auth_for_key_creation(client: AsyncClient, auth_token: str):
    """Testeaza ca un token valid poate fi folosit pentru a crea o cheie API."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post(
        "/apikeys", json={"expires_in_seconds": 3600}, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "key" in data

@pytest.mark.asyncio
async def test_expired_token_cannot_create_key(client: AsyncClient):
    """Testeaza ca un token expirat nu poate accesa resurse protejate."""
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
    Testeaza ca token-ul unui utilizator care a fost sters nu mai este valid.
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
