"""
Configuration module for application settings.
Loads sensitive settings from environment variables using Pydantic.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(".env")

class Settings(BaseSettings):
    """
    Singleton class for application settings.

    Attributes:
        APP_NAME (str): The name of the application.
        DATABASE_URL (str): The database connection URL.
        API_KEY (str): The static API key for authentication.
        API_KEY_NAME (str): The name of the API key.
        REDIS_HOST (str): The Redis host.
        REDIS_PORT (int): The Redis port.
        SECRET_KEY (str): The secret key for cryptographic operations.
        ALGORITHM (str): The algorithm used for token generation.
        ACCESS_TOKEN_EXPIRE_MINUTES (int): The expiration time for access tokens in minutes.
        REFRESH_TOKEN_EXPIRE_MINUTES (int): The expiration time for refresh tokens in minutes.
        MAX_API_KEY_LIFETIME_SECONDS (int): The maximum lifetime for API keys in seconds.
    """

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
