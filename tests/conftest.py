"""
PyTest configuration and fixtures for AMEGA-AI tests.
"""
import pytest
from fastapi.testclient import TestClient
from backend.app import app
from backend.auth import fake_users_db

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clean up the fake database after each test."""
    yield
    fake_users_db.clear() 