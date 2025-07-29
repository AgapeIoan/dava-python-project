import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.db.models import User, Base
from app.db.database import get_db
from app.core.security import get_password_hash

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# --- Fixtures for testing ---

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(DATABASE_URL, future=True)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        yield session
    await engine.dispose()

@pytest_asyncio.fixture
async def client(async_session):
    # Dependency override
    async def override_get_db():
        yield async_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_current_user(client: AsyncClient):
    # Create a user directly in the DB using the dependency override
    async for async_session in app.dependency_overrides[get_db]():
        username = "testuser"
        email = "testuser@example.com"
        password = "testpassword"
        hashed_password = get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password)
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        user_id = user.id

    # Log in to get token
    response = await client.post("/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete the current user
    response = await client.delete("/users/me", headers=headers)
    assert response.status_code == 204

    # Check user is deleted
    async for async_session in app.dependency_overrides[get_db]():
        result = await async_session.get(User, user_id)
        assert result is None

@pytest.mark.asyncio
async def test_delete_current_user_unauthenticated(client: AsyncClient):
    response = await client.delete("/users/me")
    assert response.status_code == 401
