import asyncio
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1 import schemas
from app.services.math_service import math_service
from app.db.repository import log_api_request
from app.db.database import get_db
from app.core.logging import logger
from app.core.security import get_api_key
from app.core.redis_logger import log_to_stream


router = APIRouter(tags=["Math Operations"])

@router.get("/no-block-async", tags=["Blocking Examples"], dependencies=[Depends(get_api_key)])
async def no_block_async(request: Request):
    logger.info("Intrat în /no-block-async. Încep așteptarea de 10 secunde.")
    await log_to_stream("INFO", "no-block-async started", {"path": str(request.url)})

    await asyncio.sleep(10)

    logger.info("Ieșit din /no-block-async după așteptare.")
    await log_to_stream("INFO", "no-block-async completed", {"path": str(request.url)})

    return {"message": "Am asteptat 10 secunde in mod asincron."}

@router.get("/fibonacci", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_fibonacci(
    n: int,
    request: Request,
    db: Session = Depends(get_db)
):
    await log_to_stream("INFO", "Calcul Fibonacci solicitat", {"n": n})
    logger.info("Calcul Fibonacci solicitat", input={"n": n})
    try:
        result = await math_service.fibonacci_async(n=n)

        await log_api_request(
            db=db,
            operation_type="fibonacci",
            input_params={"n": n},
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Fibonacci finalizat", result=result)
        return {"result": str(result)}
    except ValueError as e:
        logger.error("Eroare la Fibonacci", error=str(e))
        await log_to_stream("ERROR", "Eroare Fibonacci", {"error": str(e)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/power", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_power(
    base: str,
    exponent: str,
    request: Request,
    db: Session = Depends(get_db)
):
    await log_to_stream("INFO", "Calcul Power solicitat", {"base": base, "exponent": exponent})
    logger.info("Calcul Power solicitat", input={"base": base, "exponent": exponent})

    try:
        # Try to parse as float, then as complex
        def parse_number(val):
            try:
                return float(val)
            except ValueError:
                return complex(val)
        base_val = parse_number(base)
        exponent_val = parse_number(exponent)
        result = math_service.power(base=base_val, exponent=exponent_val)

        await log_api_request(
            db=db,
            operation_type="power",
            input_params={"base": base, "exponent": exponent},
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Power finalizat", result=result)
        await log_to_stream("INFO", "Calcul Power finalizat", {"result": str(result)})
        return {"result": result}
    except ValueError as e:
        logger.error("Eroare la Power", error=str(e))
        await log_to_stream("ERROR", "Eroare Power", {"error": str(e)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/factorial", response_model=schemas.MathResponse, dependencies=[Depends(get_api_key)])
async def calculate_factorial(
    n: int,
    request: Request,
    db: Session = Depends(get_db)
):
    await log_to_stream("INFO", "Calcul Factorial solicitat", {"n": n})
    logger.info("Calcul Factorial solicitat", input={"n": n})
    try:
        result = math_service.factorial(n=n)

        await log_api_request(
            db=db,
            operation_type="factorial",
            input_params={"n": n},
            result=str(result),
            client_ip=request.client.host
        )

        logger.info("Calcul Factorial finalizat", result=result)
        return {"result": result}
    except ValueError as e:
        logger.error("Eroare la Factorial", error=str(e))
        await log_to_stream("ERROR", "Eroare Factorial", {"error": str(e)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
