import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User

# Toate fixture-urile sunt acum importate implicit din conftest.py

@pytest.mark.asyncio
async def test_delete_current_user(client: AsyncClient, auth_token: str, test_user: User, db_session: AsyncSession):
    """
    Tests deleting the current authenticated user.

    Args:
        client (AsyncClient): The HTTP client for testing.
        auth_token (str): The JWT token for authentication.
        test_user (User): The test user instance.
        db_session (AsyncSession): The database session instance.

    Asserts:
        - The response status code is 204.
        - The user is removed from the database.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Stergem utilizatorul curent
    response = await client.delete("/users/me", headers=headers)
    assert response.status_code == 204

    # Verificam ca utilizatorul a fost sters din BD
    result = await db_session.get(User, test_user.id)
    assert result is None

@pytest.mark.asyncio
async def test_delete_current_user_unauthenticated(client: AsyncClient):
    """
    Tests deleting the current user without authentication.

    Args:
        client (AsyncClient): The HTTP client for testing.

    Asserts:
        - The response status code is 401.
    """
    response = await client.delete("/users/me")
    assert response.status_code == 401