import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
load_dotenv(".env")

class Settings(BaseSettings): #singleton for application settings
    """All sensitive settings **must** be supplied via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str
    DATABASE_URL: str
    API_KEY: str
    API_KEY_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    MAX_API_KEY_LIFETIME_SECONDS: int

settings = Settings()
