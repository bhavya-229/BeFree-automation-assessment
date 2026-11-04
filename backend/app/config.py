"""Application configuration settings."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings with environment variable overrides."""

    PROJECT_NAME: str = "Bank Statement Processor"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Security & Storage
    SECRET_KEY: str = "development-insecure-secret-key-change-in-production"
    DATA_DIR: Path = Path("d:/beFree/data")
    UPLOAD_DIR: Path = Path("d:/beFree/data/uploads")
    RETENTION_HOURS: int = 24
    AUTH_MODE: str = "none"  # "none" or "apikey"
    API_KEY: str = ""

    # Upload Limits
    MAX_UPLOAD_MB: int = 25
    MAX_PAGES: int = 200
    MAX_BATCH_FILES: int = 10

    # OCR Settings
    OCR_DPI: int = 300
    OCR_LANGS: str = "eng"
    OCR_TIMEOUT_SECONDS_PER_PAGE: int = 30

    # Classification Thresholds
    RULE_CONF_THRESHOLD: float = 0.80
    ML_CONF_THRESHOLD: float = 0.60

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# Ensure critical directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
