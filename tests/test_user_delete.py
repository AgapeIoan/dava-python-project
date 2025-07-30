# tests/test_user_delete.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User

# Toate fixture-urile sunt acum importate implicit din conftest.py

@pytest.mark.asyncio
async def test_delete_current_user(client: AsyncClient, auth_token: str, test_user: User, db_session: AsyncSession):
    # 'client' si 'auth_token' vin din conftest.py
    # 'test_user' ne ofera ID-ul utilizatorului pe care l-a creat auth_token
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Stergem utilizatorul curent
    response = await client.delete("/users/me", headers=headers)
    assert response.status_code == 204

    # Verificam ca utilizatorul a fost sters din BD
    result = await db_session.get(User, test_user.id)
    assert result is None

@pytest.mark.asyncio
async def test_delete_current_user_unauthenticated(client: AsyncClient):
    response = await client.delete("/users/me")
    assert response.status_code == 401