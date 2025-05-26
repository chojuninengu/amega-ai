"""
Unit tests for API models.
"""
import pytest
from pydantic import ValidationError

from amega_ai.api.models import (
    UserModel,
    APIKeyModel,
    ModelConfigurationModel,
)

def test_user_model_validation():
    """Test UserModel validation."""
    # Valid user data
    valid_data = {
        "id": "user123",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True
    }
    user = UserModel(**valid_data)
    assert user.id == valid_data["id"]
    assert user.email == valid_data["email"]
    assert user.username == valid_data["username"]
    assert user.is_active == valid_data["is_active"]

    # Invalid email
    with pytest.raises(ValidationError):
        UserModel(id="user123", email="invalid-email", username="testuser", is_active=True)

def test_api_key_model():
    """Test APIKeyModel validation."""
    valid_data = {
        "key": "sk-1234567890abcdef",
        "name": "Test Key",
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2025-01-01T00:00:00Z"
    }
    api_key = APIKeyModel(**valid_data)
    assert api_key.key == valid_data["key"]
    assert api_key.name == valid_data["name"]

def test_model_configuration():
    """Test ModelConfigurationModel validation."""
    valid_data = {
        "model_id": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 100,
        "top_p": 1.0
    }
    config = ModelConfigurationModel(**valid_data)
    assert config.model_id == valid_data["model_id"]
    assert config.temperature == valid_data["temperature"]
    assert config.max_tokens == valid_data["max_tokens"]

    # Test invalid temperature
    with pytest.raises(ValidationError):
        ModelConfigurationModel(
            model_id="gpt-3.5-turbo",
            temperature=2.0,  # Invalid: should be between 0 and 1
            max_tokens=100,
            top_p=1.0
        ) 