import secrets

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.db.models import ApiKey
from app.db.database import get_db
from app.core.security import get_api_key_hash
from app.api.v1.schemas import ApiKeyCreate, ApiKeyOut
from app.core.security import get_current_user
from app.db.models import User

router = APIRouter(prefix="/apikeys", tags=["apikeys"])

@router.post("", response_model=ApiKeyOut)
async def create_api_key(
    payload: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Genereaza o noua cheie API pentru utilizatorul autentificat.
    Daca o cheie exista deja, va fi inlocuita. Cheia secreta este afisata o singura data.
    """
    await db.execute(delete(ApiKey).where(ApiKey.user_id == current_user.id))

    prefix = f"math_{secrets.token_urlsafe(8)}"
    secret_key = secrets.token_urlsafe(32)
    
    full_key_to_display = f"{prefix}.{secret_key}"

    hashed_secret = get_api_key_hash(secret_key)

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=payload.expires_in_seconds)
    new_api_key = ApiKey(
        key_prefix=prefix,
        hashed_key=hashed_secret,
        user_id=current_user.id,
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
    )

    db.add(new_api_key)
    await db.commit()
    await db.refresh(new_api_key)

    return ApiKeyOut(
        key=full_key_to_display,
        created_at=new_api_key.created_at,
        expires_at=new_api_key.expires_at
    )
