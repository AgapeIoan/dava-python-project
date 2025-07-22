import json

from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from app.core.utils import CustomJSONEncoder

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
        input_params=json.dumps(input_params, cls=CustomJSONEncoder),
        result=result,
        client_ip=client_ip,
    )

    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    return db_request