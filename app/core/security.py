from datetime import datetime, timezone
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import ApiKey
from app.db.database import get_db

api_key_header = APIKeyHeader(name="admin_key", auto_error=False)

async def get_api_key(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    if not api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")
    result = await db.execute(select(ApiKey).where(ApiKey.key == api_key))
    record = result.scalar_one_or_none()
    if not record or record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")
    return api_key