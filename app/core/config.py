from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): #singleton for application settings
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Math Microservice"
    DATABASE_URL: str = "sqlite:///./math_service.db"
    API_KEY: str = "super_secret_api_key" #static API key for authentication
    API_KEY_NAME: str = "admin_key"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    SECRET_KEY: str = "your_secret_key"

settings = Settings()