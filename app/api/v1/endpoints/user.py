from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.core.security import get_current_user
# STERGE importul de redis_client. Nu mai avem nevoie de el aici.
# from app.services.math_service import redis_client

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
    # Nu mai este necesar sa cautam din nou utilizatorul.
    # Dependinta 'get_current_user' ne-a dat deja obiectul 'User' complet din BD.
    
    # if not current_user: # Aceasta verificare este redundanta, get_current_user ar esua inainte
    #     raise HTTPException(status_code=404, detail="User not found.")

    # Logica de stergere din Redis este acum inutila si trebuie stearsa.
    
    await db.delete(current_user)
    await db.commit()
    
    # Nu este necesar sa returnam nimic, status code-ul 204 se ocupa de asta.
    return None
