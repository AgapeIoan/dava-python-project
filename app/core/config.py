from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Math Microservice"
    DATABASE_URL: str = "sqlite:///./math_service.db"
    API_KEY: str = "super_secret_api_key"

settings = Settings()