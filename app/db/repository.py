import json
from sqlalchemy.orm import Session
from . import models

def log_api_request(
        db: Session,
        *,
        operation_type: str,
        input_params: dict,
        result: float,
        client_ip: str | None,
) -> models.ApiRequest:
    """
    Salveaza detaliile unei cereri API in baza de date.
    """
    db_request = models.ApiRequest(
        operation_type=operation_type,
        input_params=json.dumps(input_params),
        result=result,
        client_ip=client_ip,
    )

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    return db_request