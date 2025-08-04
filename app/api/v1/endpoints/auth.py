"""
Handles user authentication endpoints.
Includes signup and login functionalities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.logging import logger
from app.db.database import get_db
from app.db.models import User
from app.api.v1.schemas import UserCreate, Token
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=Token)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user.

    Args:
        user_data (UserCreate): The user data for registration.
        db (AsyncSession): The database session.

    Returns:
        dict: Access token and token type.

    Raises:
        HTTPException: If the username is already registered.
    """
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        logger.error("Username already registered", username=user_data.username)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()

    token = create_access_token(data={"sub": user_data.username})
    logger.info("User registered", username=user_data.username)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    Logs in a user and provides an access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login form data.
        db (AsyncSession): The database session.

    Returns:
        dict: Access token and token type.

    Raises:
        HTTPException: If the username or password is invalid.
    """
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.error("Invalid username or password", username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(data={"sub": user.username})
    logger.info("User logged in", username=user.username)
    return {"access_token": token, "token_type": "bearer"}