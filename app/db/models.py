from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from .database import Base

class ApiRequest(Base):
    """
    Represents an audit log of API requests.

    Attributes:
        id (int): Primary key for the API request.
        timestamp (datetime): The time the request was made.
        operation_type (str): The type of operation performed.
        input_params (str): Input parameters for the API request.
        result (str): The result of the API request.
        client_ip (str): The IP address of the client making the request. Can be null if unavailable.
    """
    __tablename__ = "api_requests"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    operation_type = Column(String, index=True)
    input_params = Column(String)
    result = Column(String)
    client_ip = Column(String, nullable=True) # Poate fi null daca nu il putem obtine

class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for the user.
        created_at (datetime): Timestamp when the user was created.
        api_keys (relationship): Relationship to the user's API keys.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")

class ApiKey(Base):
    """
    Represents an API key associated with a user.

    Attributes:
        id (int): Primary key for the API key.
        key_prefix (str): Unique prefix for the API key.
        hashed_key (str): Hashed secret part of the API key.
        user_id (int): Foreign key linking the API key to a user.
        created_at (datetime): Timestamp when the API key was created.
        expires_at (datetime): Expiration timestamp for the API key.
        user (relationship): Relationship to the associated user.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_prefix = Column(String, unique=True, index=True, nullable=False)
    hashed_key = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="api_keys") # 1 to 1 relationship with User
