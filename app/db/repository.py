import json
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from . import models
from app.core.utils import CustomJSONEncoder

logger = logging.getLogger("db_operations")

async def log_api_request(
        db: AsyncSession,
        *,
        operation_type: str,
        input_params: dict,
        result: str,
        client_ip: str | None,
) -> models.ApiRequest:
    """
    Saves an API request to the database for auditing purposes.
    """
    try:
        db_request = models.ApiRequest(
            operation_type=operation_type,
            input_params=json.dumps(input_params, cls=CustomJSONEncoder),
            result=result,
            client_ip=client_ip,
        )

        db.add(db_request) #add the request to the session
        await db.commit() #commit the session to save the request
        await db.refresh(db_request) #refresh the instance to get the updated state from the database

        return db_request #return the saved request instance
    except SQLAlchemyError as e:
        logger.error(f"Failed to log API request: {e}")
        await db.rollback() #rollback the session in case of failure
        raise