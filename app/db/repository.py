from sqlalchemy.ext.asyncio import AsyncSession
from . import models

async def make_json_serializable(obj):
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    return obj

async def log_api_request(
        db: AsyncSession,
        *,
        operation_type: str,
        input_params: dict,
        result: str,
        client_ip: str | None,
) -> models.ApiRequest:
    """
    Salveaza detaliile unei cereri API in baza de date.
    """
    db_request = models.ApiRequest(
        operation_type=operation_type,
        input_params=str(make_json_serializable(input_params)),
        result=result,
        client_ip=client_ip,
    )

    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    return db_request