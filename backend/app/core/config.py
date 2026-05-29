"""Application configuration, driven entirely by environment variables.

Uses pydantic-settings so the same code runs against PostgreSQL (production,
Docker, Render) or SQLite (zero-setup local dev) purely by changing
``DATABASE_URL``. Nothing else in the app needs to know which backend is used.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # Allow a field named ``model_dir`` without pydantic's model_ guard.
        protected_namespaces=(),
    )

    # --- Application ---
    app_name: str = "SecondPlate"
    environment: str = "development"
    api_prefix: str = "/api"
    log_level: str = "info"

    # --- Database ---
    # Default is SQLite so the project boots with zero external dependencies.
    # Docker/Render override this with a postgresql+psycopg2://... URL.
    database_url: str = "sqlite:///./local.db"

    # --- CORS ---
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # --- ML ---
    model_dir: str = "app/ml/artifacts"

    # --- Seed ---
    seed_on_startup: bool = False
    seed_random_state: int = 42

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        """Accept a comma-separated string from the environment."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
