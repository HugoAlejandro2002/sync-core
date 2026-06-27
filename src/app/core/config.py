from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "Caja Inteligente API"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True

    DATABASE_URL: str = "mysql+asyncmy://root:password@localhost:3306/caja_inteligente"

    GEMINI_API_KEY: str = "replace-me"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    MEDIA_STORAGE_DRIVER: str = "local"
    LOCAL_MEDIA_DIR: str = "./storage/media"

    DEFAULT_CURRENCY: str = "BOB"
    TIMEZONE: str = "America/La_Paz"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
