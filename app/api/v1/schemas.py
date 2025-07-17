from pydantic import BaseModel, Field

class MathResponse(BaseModel):
    result: float

class FibonacciRequest(BaseModel):
    n: int = Field(..., ge=0, le=90, description="The index of the Fibonacci number (0 <= n <= 90).")

class FactorialRequest(BaseModel):
    # Folosim Field pentru validari mai avansate, direct in schema
    n: int = Field(..., ge=0, le=20, description="The number for the factorial (0 <= n <= 20).")

# ... aici vor veni si celelalte scheme (PowerRequest, FactorialRequest) ...```