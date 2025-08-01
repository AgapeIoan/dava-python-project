from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
from app.core.logging import logger

router = APIRouter(prefix="/users", tags=["Users"])

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Sterge utilizatorul autentificat curent.
    Datorita relatiei 'CASCADE' din model, orice cheie API asociata
    va fi stearsa automat de baza de date.
    """
    await db.delete(current_user)
    await db.commit()
    
    logger.info("User deleted", user_id=current_user.id)
    return None
