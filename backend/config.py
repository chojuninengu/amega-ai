"""
Configuration module for AMEGA-AI

This module handles configuration loading from environment variables and provides
type-safe configuration objects.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, validator

class Settings(BaseSettings):
    """Application settings."""
    # App settings
    APP_NAME: str = "AMEGA-AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DATABASE_URL: Optional[PostgresDsn] = None
    
    # Model settings
    MODEL_NAME: str = "microsoft/DialoGPT-medium"
    
    # JWT settings
    SECRET_KEY: str = Field(default="your-secret-key-please-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="AMEGA_"
    )
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate database URL if provided."""
        if isinstance(v, str):
            return v
        return None

# Global settings instance
settings = Settings() 