"""
Unit tests for the configuration module.
"""

import os
from pathlib import Path
import pytest
from pydantic import ValidationError
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

def test_settings_defaults(mock_settings):
    """Test default configuration values."""
    assert mock_settings.APP_NAME == "Amega AI"
    assert mock_settings.VERSION == "0.1.0"
    assert mock_settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert mock_settings.api.HOST == "0.0.0.0"
    assert mock_settings.api.PORT == 8000
    assert mock_settings.llm.BACKEND == LLMBackend.OLLAMA
    assert mock_settings.llm.DEFAULT_MODEL == "llama2"
    assert mock_settings.logging.LEVEL == LogLevel.INFO

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