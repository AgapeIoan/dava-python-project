from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
load_dotenv(".env")

class Settings(BaseSettings): #singleton for application settings
    """All sensitive settings **must** be supplied via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Math Microservice"
    DATABASE_URL: str = "sqlite:///./math_service.db"
    API_KEY: str = "test_api_key"
    API_KEY_NAME: str = "X-API-Key"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    SECRET_KEY: str = "test_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    MAX_API_KEY_LIFETIME_SECONDS: int = 86400

settings = Settings()
