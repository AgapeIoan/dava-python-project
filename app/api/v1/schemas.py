from pydantic import BaseModel, Field
from datetime import datetime

class MathResponse(BaseModel):
    result: float|complex

class FibonacciRequest(BaseModel):
    n: int = Field(..., ge=0, le=90, description="The index of the Fibonacci number (0 <= n <= 90).")

class PowerRequest(BaseModel):
    base: float|complex = Field(description='The base number for exponentiation. Can be real or complex.')
    exponent: float|complex = Field(description='The exponent for the base number. Can be real or complex.')

class FactorialRequest(BaseModel):
    # Folosim Field pentru validari mai avansate, direct in schema
    n: int = Field(..., ge=0, le=20, description="The number for the factorial (0 <= n <= 20).")

class ApiKeyCreate(BaseModel):
    expires_in_seconds: int

class ApiKeyOut(BaseModel):
    key: str
    created_at: datetime
    expires_at: datetime

    class Config:
        orm_mode = True
