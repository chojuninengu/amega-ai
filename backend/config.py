"""
Configuration Module for Amega AI Backend.

This module handles loading and validation of all environment variables and
configuration settings needed for the backend application.
"""

from typing import Optional, Dict, Any
import os
from enum import Enum
from pathlib import Path
from pydantic import BaseSettings, Field, PostgresDsn, validator
from pydantic.networks import AnyHttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Environment(str, Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class LogLevel(str, Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LLMBackend(str, Enum):
    """Supported LLM backends."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    URL: PostgresDsn = Field(..., env="DB_URL")
    POOL_SIZE: int = Field(default=5, env="DB_POOL_SIZE")
    MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    ECHO: bool = Field(default=False, env="DB_ECHO")

    class Config:
        case_sensitive = True

class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    CORS_ORIGINS: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    SSL_KEYFILE: Optional[Path] = Field(default=None, env="SSL_KEYFILE")
    SSL_CERTFILE: Optional[Path] = Field(default=None, env="SSL_CERTFILE")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        case_sensitive = True

class APISettings(BaseSettings):
    """API configuration settings."""
    HOST: str = Field(default="0.0.0.0", env="API_HOST")
    PORT: int = Field(default=8000, env="API_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ROOT_PATH: str = Field(default="", env="API_ROOT_PATH")
    DOCS_URL: Optional[str] = Field(default="/docs", env="API_DOCS_URL")
    OPENAPI_URL: Optional[str] = Field(default="/openapi.json", env="API_OPENAPI_URL")

    class Config:
        case_sensitive = True

class LLMSettings(BaseSettings):
    """LLM configuration settings."""
    BACKEND: LLMBackend = Field(default=LLMBackend.OLLAMA, env="LLM_BACKEND")
    API_KEY: Optional[str] = Field(default=None, env="LLM_API_KEY")
    API_URL: Optional[AnyHttpUrl] = Field(default=None, env="LLM_API_URL")
    DEFAULT_MODEL: str = Field(default="llama2", env="LLM_DEFAULT_MODEL")
    MAX_TOKENS: int = Field(default=1000, env="LLM_MAX_TOKENS")
    TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")

    class Config:
        case_sensitive = True

class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    FILE: Optional[Path] = Field(default=None, env="LOG_FILE")
    FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    MAX_BYTES: int = Field(default=10*1024*1024, env="LOG_MAX_BYTES")  # 10MB
    BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")

    class Config:
        case_sensitive = True

class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    SSL: bool = Field(default=False, env="REDIS_SSL")
    SSL_CERT_REQS: Optional[str] = Field(default=None, env="REDIS_SSL_CERT_REQS")

    class Config:
        case_sensitive = True

class Settings(BaseSettings):
    """Main configuration settings."""
    # Basic settings
    APP_NAME: str = Field(default="Amega AI", env="APP_NAME")
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    VERSION: str = Field(default="0.1.0", env="VERSION")
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    security: SecuritySettings = SecuritySettings()
    api: APISettings = APISettings()
    llm: LLMSettings = LLMSettings()
    logging: LoggingSettings = LoggingSettings()
    redis: RedisSettings = RedisSettings()

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MODELS_DIR: Path = Field(default=Path("models"), env="MODELS_DIR")
    DATA_DIR: Path = Field(default=Path("data"), env="DATA_DIR")
    CACHE_DIR: Path = Field(default=Path("cache"), env="CACHE_DIR")

    @validator("MODELS_DIR", "DATA_DIR", "CACHE_DIR", pre=True)
    def create_directory(cls, v: Path) -> Path:
        """Create directory if it doesn't exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get settings instance."""
    return settings 