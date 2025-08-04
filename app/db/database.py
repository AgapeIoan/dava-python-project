from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.core.logging import logger

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,  # Adjust pool size as needed
    max_overflow=20,  # Allow some overflow connections
    pool_pre_ping=True,  # Check connections before using them
)
"""
Creates an asynchronous SQLAlchemy engine.

This engine is configured with connection pooling and pre-ping checks to ensure
connections are valid before use.

Args:
    settings.DATABASE_URL (str): The database connection URL.
    pool_size (int): The number of connections to keep in the pool.
    max_overflow (int): The number of additional connections allowed beyond the pool size.
    pool_pre_ping (bool): Enables pre-ping checks for connections.
"""

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False #keeps the data accessible after commit
)
"""
Creates an asynchronous session maker.

This session maker binds the engine and ensures data remains accessible after commit.

Args:
    bind (Engine): The SQLAlchemy engine to bind.
    class_ (Type): The class to use for sessions.
    expire_on_commit (bool): Prevents data from expiring after commit.
"""

Base = declarative_base()
"""
Defines the base class for SQLAlchemy models.

This base class is used to declare database models.
"""

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async DB session.

    This function provides an asynchronous database session for use in FastAPI endpoints.

    Yields:
        AsyncSession: The database session.

    Logs:
        Opening and closing of the database session.
    """
    logger.info("Opening a new database session.")
    async with AsyncSessionLocal() as session:
        yield session
    logger.info("Closing the database session.")