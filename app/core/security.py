from datetime import datetime, timezone, timedelta
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.db.models import User
from app.db.database import get_db
from app.api.v1.schemas import TokenData
from app.services.math_service import redis_client
from app.core.utils import verify_api_key
from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated="auto",
    argon2__memory_cost=65536,
    argon2__time_cost=3,
    argon2__parallelism=4
)

api_key_header = APIKeyHeader(name="admin_key", auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
    data: dict, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    to_encode.update({"iat": now, "iss": "your-api-name", "sub": data.get("sub")})
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp", "sub", "iat"]})
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == token_data.username))
    print(f"User found: {result}")  # Debugging line to check user retrieval
    user = result.scalar_one_or_none()
    print(f"Current user: {user}")  # Debugging line to check current user
    if user is None:
        raise credentials_exception
    return user

async def get_api_key(
    api_key: str = Security(api_key_header),
):
    if not api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")

    # Use Redis as secure store for API key hashes and expiry

    if not redis_client:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "API key store unavailable")

    # The API key is now in the format key_id.raw_key
    try:
        key_id, raw_key = api_key.split(".", 1)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")

    redis_key = f"apikey:{key_id}"
    data = await redis_client.get(redis_key)
    if not data:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")
    try:
        data = json.loads(data)
        hashed_key = data["hash"]
        expires_at = datetime.fromisoformat(data["expires_at"])
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")

    if not verify_api_key(raw_key, hashed_key):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")
    if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API Key")
    return api_key