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
    Logs an API request to the database for auditing purposes.

    This function saves details of an API request, including its operation type,
    input parameters, result, and client IP address, to the database.

    Args:
        db (AsyncSession): The database session used for the operation.
        operation_type (str): The type of operation performed by the API.
        input_params (dict): The input parameters provided to the API.
        result (str): The result returned by the API.
        client_ip (str | None): The IP address of the client making the request.

    Returns:
        models.ApiRequest: The saved API request instance.

    Raises:
        SQLAlchemyError: If the operation fails, an exception is raised and the session is rolled back.
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