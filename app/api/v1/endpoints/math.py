from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1 import schemas
from app.services.math_service import math_service
from app.db.repository import log_api_request
from app.db.database import get_db

router = APIRouter(tags=["Math Operations"])

@router.post("/fibonacci", response_model=schemas.MathResponse)
def calculate_fibonacci(
        req_body: schemas.FibonacciRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """
    Calculates the n-th Fibonacci number.
    """
    try:
        result = math_service.fibonacci(n=req_body.n)

        log_api_request(
            db=db,
            operation_type="fibonacci",
            input_params=req_body.dict(),
            result=result,
            client_ip=request.client.host
        )

        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))