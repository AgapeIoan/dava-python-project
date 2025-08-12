"""
Defines Pydantic schemas for API requests and responses.
Includes models for mathematical operations, API key management, and user authentication.
"""

from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

class MathResponse(BaseModel):
    """
    Schema for mathematical operation responses.

    Attributes:
        result (float|complex): The result of the mathematical operation.
    """
    result: float|complex

class ApiKeyCreate(BaseModel):
    """
    Schema for creating an API key.

    Attributes:
        expires_in_seconds (int): The duration in seconds for which the API key is valid.
    """
    expires_in_seconds: int

class ApiKeyOut(BaseModel):
    """
    Schema for API key response.

    Attributes:
        key (str): The API key.
        created_at (datetime): The creation timestamp of the API key.
        expires_at (datetime): The expiration timestamp of the API key.
    """
    key: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class UserCreate(BaseModel):
    """
    Schema for user creation.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        password (str): The password for the user.
    """
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    """
    Schema for authentication token response.

    Attributes:
        access_token (str): The access token.
        token_type (str): The type of the token (default is "bearer").
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema for token data.

    Attributes:
        username (str | None): The username associated with the token.
    """
    username: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True