from pydantic import BaseModel, Field

class MathResponse(BaseModel):
    result: float

class FibonacciRequest(BaseModel):
    n: int = Field(..., ge=0, le=90, description="The index of the Fibonacci number (0 <= n <= 90).")

# ... aici vor veni si celelalte scheme (PowerRequest, FactorialRequest) ...```