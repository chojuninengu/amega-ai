"""
Tests for API models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.llm_manager import ChatMessage
from backend.auth import User, Token

def test_chat_message_model():
    """Test ChatMessage model validation."""
    # Test valid message
    message = ChatMessage(
        role="user",
        content="Hello, AI!"
    )
    assert message.role == "user"
    assert message.content == "Hello, AI!"
    assert isinstance(message.timestamp, datetime)
    
    # Test invalid role
    with pytest.raises(ValidationError):
        ChatMessage(
            role="invalid_role",
            content="Test message"
        )
    
    # Test empty content
    with pytest.raises(ValidationError):
        ChatMessage(
            role="user",
            content=""
        )

def test_user_model():
    """Test User model validation."""
    # Test valid user
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.disabled is False

    # Test invalid email
    with pytest.raises(ValidationError):
        User(
            username="testuser",
            email="invalid_email"
        )
    
    # Test missing required fields
    with pytest.raises(ValidationError):
        User()

def test_token_model():
    """Test Token model validation."""
    # Test valid token
    token = Token(
        access_token="test_token",
        token_type="bearer"
    )
    assert token.access_token == "test_token"
    assert token.token_type == "bearer"

    # Test missing required fields
    with pytest.raises(ValidationError):
        Token() 