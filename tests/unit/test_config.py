"""
Unit tests for the configuration module.
"""

import os
from pathlib import Path
import pytest
from pydantic import ValidationError, PostgresDsn
from backend.config import (
    Settings,
    Environment,
    LogLevel,
    LLMBackend,
    get_settings,
)

@pytest.fixture
def env_vars():
    """Set up test environment variables."""
    old_env = dict(os.environ)
    test_env = {
        "ENVIRONMENT": "testing",
        "DB_URL": "postgresql://test:test@localhost:5432/test_db",
        "JWT_SECRET_KEY": "test-secret-key",
        "REDIS_URL": "redis://localhost:6379",
        "LLM_BACKEND": "ollama",
        "LOG_LEVEL": "DEBUG"
    }
    os.environ.update(test_env)
    yield test_env
    os.environ.clear()
    os.environ.update(old_env)

@pytest.fixture
def mock_settings():
    """Create test settings with minimal required config."""
    return Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={"SECRET_KEY": "test-secret-key"}
    )

def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.APP_NAME == "AMEGA-AI"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.DEBUG is False
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.MODEL_NAME == "microsoft/DialoGPT-medium"
    assert settings.SECRET_KEY == "your-secret-key-please-change-in-production"
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30

def test_settings_env_override(monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("AMEGA_APP_NAME", "Test App")
    monkeypatch.setenv("AMEGA_DEBUG", "true")
    monkeypatch.setenv("AMEGA_PORT", "9000")
    
    settings = Settings()
    assert settings.APP_NAME == "Test App"
    assert settings.DEBUG is True
    assert settings.PORT == 9000

def test_database_url_validation():
    """Test database URL validation."""
    valid_url = "postgresql://user:pass@localhost:5432/db"
    settings = Settings(DATABASE_URL=valid_url)
    assert isinstance(settings.DATABASE_URL, PostgresDsn)
    assert str(settings.DATABASE_URL) == valid_url

def test_allowed_origins():
    """Test ALLOWED_ORIGINS setting."""
    settings = Settings()
    assert isinstance(settings.ALLOWED_ORIGINS, list)
    assert len(settings.ALLOWED_ORIGINS) > 0
    assert all(isinstance(origin, str) for origin in settings.ALLOWED_ORIGINS)

def test_settings_from_env(env_vars):
    """Test loading configuration from environment variables."""
    settings = Settings(
        database={"URL": env_vars["DB_URL"]},
        security={"SECRET_KEY": env_vars["JWT_SECRET_KEY"]}
    )
    assert settings.ENVIRONMENT == Environment.TESTING
    assert str(settings.database.URL) == env_vars["DB_URL"]
    assert settings.security.SECRET_KEY == env_vars["JWT_SECRET_KEY"]
    assert settings.redis.URL == env_vars["REDIS_URL"]
    assert settings.llm.BACKEND == LLMBackend.OLLAMA
    assert settings.logging.LEVEL == LogLevel.DEBUG

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip in CI environment")
def test_required_settings():
    """Test validation of required settings."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(database={"URL": None}, security={"SECRET_KEY": None})
    assert "DB_URL" in str(exc_info.value)
    assert "JWT_SECRET_KEY" in str(exc_info.value)

def test_cors_origins_parsing(mock_settings):
    """Test CORS origins parsing from string."""
    settings = Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={
            "SECRET_KEY": "test-secret-key",
            "CORS_ORIGINS": "http://localhost,https://example.com"
        }
    )
    assert settings.security.CORS_ORIGINS == ["http://localhost", "https://example.com"]

    settings = Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={
            "SECRET_KEY": "test-secret-key",
            "CORS_ORIGINS": ["http://localhost"]
        }
    )
    assert settings.security.CORS_ORIGINS == ["http://localhost"]

@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip in CI environment")
def test_directory_creation():
    """Test automatic directory creation."""
    test_dir = Path("test_data")
    settings = Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={"SECRET_KEY": "test-secret-key"},
        MODELS_DIR=test_dir
    )
    assert test_dir.exists()
    assert test_dir.is_dir()
    test_dir.rmdir()  # Clean up

def test_get_settings(mock_settings):
    """Test get_settings function returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Singleton pattern

def test_llm_settings_validation(mock_settings):
    """Test LLM settings validation."""
    settings = Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={"SECRET_KEY": "test-secret-key"},
        llm={"BACKEND": "openai"}
    )
    assert settings.llm.BACKEND == LLMBackend.OPENAI

    with pytest.raises(ValidationError):
        Settings(
            database={"URL": "postgresql://test:test@localhost:5432/test_db"},
            security={"SECRET_KEY": "test-secret-key"},
            llm={"BACKEND": "invalid_backend"}
        )

def test_logging_settings(mock_settings):
    """Test logging settings configuration."""
    log_file = Path("test.log")
    settings = Settings(
        database={"URL": "postgresql://test:test@localhost:5432/test_db"},
        security={"SECRET_KEY": "test-secret-key"},
        logging={
            "LEVEL": "ERROR",
            "FILE": log_file,
            "FORMAT": "%(message)s"
        }
    )
    assert settings.logging.LEVEL == LogLevel.ERROR
    assert settings.logging.FILE == log_file
    assert settings.logging.FORMAT == "%(message)s"

def test_database_settings():
    """Test database settings configuration."""
    settings = Settings(
        database={
            "URL": "postgresql://test:test@localhost:5432/test_db",
            "POOL_SIZE": 10,
            "MAX_OVERFLOW": 20,
            "ECHO": True
        },
        security={"SECRET_KEY": "test-secret-key"}
    )
    assert str(settings.database.URL) == "postgresql://test:test@localhost:5432/test_db"
    assert settings.database.POOL_SIZE == 10
    assert settings.database.MAX_OVERFLOW == 20
    assert settings.database.ECHO is True 