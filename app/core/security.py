from datetime import datetime, timezone, timedelta
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.db.models import User
from app.db.database import get_db
from app.api.v1.schemas import TokenData
from app.core.config import settings
from app.db.models import ApiKey

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    default="argon2",
    deprecated="auto"
)

api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

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
    api_key_str: str | None = Security(api_key_header_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Valideaza o cheie API. Gaseste cheia dupa prefix si verifica hash-ul partii secrete.
    """
    print(f"[DEBUG] get_api_key: api_key_str primit = {api_key_str}")
    if not api_key_str:
        print("[DEBUG] get_api_key: lipseste cheia API")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "API Key is missing")

    try:
        prefix, secret_key = api_key_str.rsplit(".", 1)
        print(f"[DEBUG] get_api_key: prefix = {prefix}, secret_key = {secret_key}")
    except ValueError:
        print("[DEBUG] get_api_key: format invalid pentru cheia API")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid API Key format")

    result = await db.execute(select(ApiKey).where(ApiKey.key_prefix == prefix))
    record = result.scalar_one_or_none()
    print(f"[DEBUG] get_api_key: record gasit in DB = {record}")

    if not record:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid or expired API Key")

    now_aware = datetime.now(timezone.utc)
    expires_at_aware = record.expires_at.replace(tzinfo=timezone.utc)

    if expires_at_aware < now_aware:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid or expired API Key")

    if not verify_api_key(secret_key, record.hashed_key):
        print("[DEBUG] get_api_key: hash-ul cheii nu se potriveste")
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid or expired API Key")

    print("[DEBUG] get_api_key: cheia API este valida")

def get_api_key_hash(api_key: str):
    """Face hash la partea secreta a unei chei API."""
    return pwd_context.hash(api_key)

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verifica o cheie API in text clar cu varianta ei hash-uita."""
    return pwd_context.verify(plain_api_key, hashed_api_key)