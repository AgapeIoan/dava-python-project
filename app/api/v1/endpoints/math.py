import asyncio
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1 import schemas
from app.services.math_service import math_service
from app.db.repository import log_api_request
from app.db.database import get_db
from app.core.logging import logger
from app.core.security import get_api_key

router = APIRouter(tags=["Math Operations"])

@router.get("/no-block-async", tags=["Blocking Examples"], dependencies=[Depends(get_api_key)])
async def no_block_async():
    """
    Simuleaza o operatiune I/O non-blocanta.
    """
    logger.info("Intrat în /no-block-async. Încep așteptarea de 10 secunde.")
    await asyncio.sleep(10)
    logger.info("Ieșit din /no-block-async după așteptare.")
    return {"message": "Am asteptat 10 secunde in mod asincron."}

@router.post("/fibonacci", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_fibonacci(
    req_body: schemas.FibonacciRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    logger.info("Calcul Fibonacci solicitat", input=req_body.model_dump())
    try:
        result = math_service.fibonacci(n=req_body.n)

        await log_api_request(
            db=db,
            operation_type="fibonacci",
            input_params=req_body.model_dump(),
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Fibonacci finalizat", result=result)
        return {"result": result}
    except ValueError as e:
        logger.error("Eroare la Fibonacci", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/power", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_power(
    req_body: schemas.PowerRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    logger.info("Calcul Power solicitat", input=req_body.model_dump())
    try:
        result = math_service.power(base=req_body.base, exponent=req_body.exponent)

        await log_api_request(
            db=db,
            operation_type="power",
            input_params=req_body.model_dump(),
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Power finalizat", result=result)
        return {"result": result}
    except ValueError as e:
        logger.error("Eroare la Power", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/factorial", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_factorial(
    req_body: schemas.FactorialRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    logger.info("Calcul Factorial solicitat", input=req_body.model_dump())
    try:
        result = math_service.factorial(n=req_body.n)

        await log_api_request(
            db=db,
            operation_type="factorial",
            input_params=req_body.model_dump(),
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Factorial finalizat", result=result)
        return {"result": result}
    except ValueError as e:
        logger.error("Eroare la Factorial", error=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
