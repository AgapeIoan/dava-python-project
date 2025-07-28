from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ApiKey
from app.api.v1.schemas import ApiKeyCreate, ApiKeyOut
from app.db.database import get_db
from app.core.security import get_current_user
from app.db.models import User


router = APIRouter(prefix="/apikeys", tags=["apikeys"])

@router.post("", response_model=ApiKeyOut)
async def create_api_key(
    payload: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expires_at = datetime.now(UTC) + timedelta(seconds=payload.expires_in_seconds)
    new_key = ApiKey(expires_at=expires_at, user_id=current_user.id)
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    return new_key
