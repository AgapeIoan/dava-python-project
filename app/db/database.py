from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,  # Adjust pool size as needed
    max_overflow=20,  # Allow some overflow connections
    pool_pre_ping=True,  # Check connections before using them
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False #keeps the data accessible after commit
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency to get an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session