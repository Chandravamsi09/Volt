"""
Volt Platform Core Settings & Configuration Module
"""

import json
from pathlib import Path
from typing import Any, List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for Volt AI/ML & Data Platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    # General Platform Settings
    PROJECT_NAME: str = "Volt"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "insecure-secret-key-for-dev-change-in-production-min-32-chars"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 Hours
    ALGORITHM: str = "HS256"

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                return [v]
        return v

    # PostgreSQL Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "volt_admin"
    POSTGRES_PASSWORD: str = "volt_secure_password"
    POSTGRES_DB: str = "volt_db"
    DATABASE_URL: Optional[str] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Any) -> str:
        if isinstance(v, str) and v.strip():
            return v
        # Fallback to in-memory/file sqlite for development/testing if postgres unavailable
        return "sqlite+aiosqlite:///./volt.db"

    # Redis Cache & Broker
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery Task Queue
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Data Lakehouse & Local Storage Paths
    DATA_LAKE_PATH: str = "./data/lakehouse"
    OFFLINE_FEATURE_STORE_PATH: str = "./data/feature_store"
    DUCKDB_PATH: str = "./data/duckdb/volt_analytics.duckdb"
    MODEL_VAULT_PATH: str = "./data/model_vault"

    # Qdrant Vector Store
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: Optional[str] = None

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"

    # Observability & Drift
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    DRIFT_DETECTION_INTERVAL_HOURS: int = 6
    DRIFT_PSI_THRESHOLD: float = 0.25
    DRIFT_KS_PVALUE_THRESHOLD: float = 0.05

    def ensure_directories(self) -> None:
        """Ensure necessary runtime storage directories exist."""
        for path_str in [
            self.DATA_LAKE_PATH,
            self.OFFLINE_FEATURE_STORE_PATH,
            Path(self.DUCKDB_PATH).parent.as_posix(),
            self.MODEL_VAULT_PATH,
        ]:
            Path(path_str).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
