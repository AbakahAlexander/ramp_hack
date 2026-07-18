from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Crux API"
    environment: str = "development"
    secret_key: str = "dev-secret-change-in-production"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"
    database_url: str = "sqlite:///./crux.db"
    cors_origins: str = "*"
    seed_on_startup: bool = True
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
