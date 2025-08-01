from pydantic_settings import BaseSettings, SettingsConfigDict

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

settings = Settings()