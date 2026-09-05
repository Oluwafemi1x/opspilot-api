from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpsPilot API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./opspilot.db"
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        if not isinstance(value, str):
            return value
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @model_validator(mode="after")
    def validate_production_database(self):
        if self.app_env.lower() == "production" and not self.database_url.startswith(
            "postgresql+psycopg://"
        ):
            raise ValueError("Production requires a PostgreSQL DATABASE_URL")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
