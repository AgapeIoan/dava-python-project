import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from unittest.mock import patch

from app.main import app
from app.db.database import Base, get_db
from app.db.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="session")
async def engine():
    return create_async_engine(TEST_DATABASE_URL)

@pytest_asyncio.fixture(scope="function")
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(engine, setup_database):
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """
    Un client de test care suprascrie dependenta de BD si "peticeste" (mocks)
    clientii Redis la momentul importului.
    """
    app.dependency_overrides[get_db] = lambda: db_session
    
    with patch("app.core.redis_cache.cache") as _, \
         patch("app.core.redis_logger.redis_client") as _:

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """Creeaza un utilizator de test direct in BD si il returneaza."""
    from app.core.security import get_password_hash
    from app.db.models import User

    user = User(
        username="testuser_api",
        email="testapi@example.com",
        hashed_password=get_password_hash("StrongPassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture(scope="function")
async def auth_token(client: AsyncClient, test_user: User):
    """Se logheaza cu utilizatorul de test si returneaza un token JWT."""
    response = await client.post(
        "/auth/login",
        data={"username": test_user.username, "password": "StrongPassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture(scope="function")
async def api_key_headers(client: AsyncClient, auth_token: str):
    """Genereaza o cheie API noua si returneaza header-ul de autentificare."""
    jwt_headers = {"Authorization": f"Bearer {auth_token}"}
    response = await client.post(
        "/apikeys", json={"expires_in_seconds": 60}, headers=jwt_headers
    )
    assert response.status_code == 200
    api_key = response.json()["key"]
    return {"X-API-Key": api_key}