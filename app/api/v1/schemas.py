from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime

class MathResponse(BaseModel):
    result: float|complex

class ApiKeyCreate(BaseModel):
    expires_in_seconds: int

class ApiKeyOut(BaseModel):
    key: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
