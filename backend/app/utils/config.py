"""
Configuration management for Sentiment Space backend.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Optional


class Config:
    """Backend configuration loaded from environment."""

    # FastAPI Settings
    FASTAPI_ENV: str = os.getenv("FASTAPI_ENV", "development")
    FASTAPI_DEBUG: bool = os.getenv("FASTAPI_DEBUG", "true").lower() == "true"
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "./data/sentiment.db")

    # LLM Configuration
    LLM_MODEL_NAME: str = os.getenv(
        "LLM_MODEL_NAME", "meta-llama/Llama-2-7b-hf"
    )
    LLM_QUANTIZATION: str = os.getenv("LLM_QUANTIZATION", "int4")
    LLM_DEVICE: str = os.getenv("LLM_DEVICE", "cpu")
    LLM_MAX_NEW_TOKENS: int = int(os.getenv("LLM_MAX_NEW_TOKENS", "256"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "1"))

    # S3 Export (Optional)
    S3_ENABLED: bool = os.getenv("S3_ENABLED", "false").lower() == "true"
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv(
        "AWS_SECRET_ACCESS_KEY"
    )
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "sentiment-space")

    # Logging
    LOG_LATENCY: bool = os.getenv("LOG_LATENCY", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Validate critical configuration settings."""
        if cls.S3_ENABLED:
            if not cls.AWS_ACCESS_KEY_ID or not cls.AWS_SECRET_ACCESS_KEY:
                raise ValueError(
                    "S3_ENABLED=true requires AWS credentials in .env"
                )

    @classmethod
    def to_dict(cls) -> dict:
        """Return all config as dictionary."""
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("_") and k.isupper()
        }
