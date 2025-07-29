from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
from app.services.math_service import redis_client

router = APIRouter(prefix="/users", tags=["Users"])

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Delete the currently authenticated user
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Delete API key from Redis if exists
    if redis_client:
        user_key_map = f"user_apikey:{user.id}"
        key_id = await redis_client.get(user_key_map)
        if key_id:
            await redis_client.delete(f"apikey:{key_id}")
            await redis_client.delete(user_key_map)
    await db.delete(user)
    await db.commit()
    return None
