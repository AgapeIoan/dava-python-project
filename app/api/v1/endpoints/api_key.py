from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends
import json
import secrets
import uuid
from app.api.v1.schemas import ApiKeyCreate, ApiKeyOut
from app.core.security import get_current_user
from app.db.models import User
from app.services.math_service import redis_client
from app.core.utils import hash_api_key

router = APIRouter(prefix="/apikeys", tags=["apikeys"])

@router.post("", response_model=ApiKeyOut)
async def create_api_key(
    payload: ApiKeyCreate,
    current_user: User = Depends(get_current_user)
):

    expires_at = datetime.now(UTC) + timedelta(seconds=payload.expires_in_seconds)
    created_at = datetime.now(UTC)

    key_id = uuid.uuid4().hex
    raw_key = secrets.token_urlsafe(32)
    api_key = f"{key_id}.{raw_key}"

    hashed_key = hash_api_key(raw_key)
    redis_key = f"apikey:{key_id}"
    value = json.dumps({
        "hash": hashed_key,
        "expires_at": expires_at.isoformat()
    })
    if redis_client:
        # Enforce one valid API key per user
        user_key_map = f"user_apikey:{current_user.id}"
        old_key_id = await redis_client.get(user_key_map)
        if old_key_id:
            await redis_client.delete(f"apikey:{old_key_id}")
        await redis_client.set(redis_key, value, ex=payload.expires_in_seconds)
        await redis_client.set(user_key_map, key_id, ex=payload.expires_in_seconds)

    return ApiKeyOut(
        key=api_key,
        created_at=created_at,
        expires_at=expires_at
    )
