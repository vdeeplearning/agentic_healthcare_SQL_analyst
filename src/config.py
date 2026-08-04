"""Application configuration."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings; secrets are never serialized to audit logs."""

    model_config = SettingsConfigDict(env_prefix="CLINICAL_SQL_", env_file=".env", extra="ignore")
    db_path: Path = Path("data/generated/clinical.db")
    demo_mode: bool = True
    seed: int = 42
    query_timeout_seconds: float = 5.0
    max_rows: int = 1000
    max_joins: int = 8
    max_selected_columns: int = 20
    small_cell_threshold: int = 10
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-sol"


@lru_cache
def get_settings() -> Settings:
    return Settings()
