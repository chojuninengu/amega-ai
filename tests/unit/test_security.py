"""Tests for security middleware and RBAC functionality."""
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from backend.security import (
    SecurityMiddleware, RBACMiddleware, RequestValidationMiddleware,
    requires_admin, requires_moderator, requires_user
)
from backend.auth import User, get_current_user

# Test app setup
app = FastAPI()
app.add_middleware(SecurityMiddleware)
app.add_middleware(RBACMiddleware)
app.add_middleware(RequestValidationMiddleware)

# Mock endpoints for testing
@app.get("/test/public")
async def public_endpoint():
    return {"message": "public"}

@app.get("/test/user")
async def user_endpoint(user: User = Depends(requires_user)):
    return {"message": "user", "role": user.role}

@app.get("/test/moderator")
async def moderator_endpoint(user: User = Depends(requires_moderator)):
    return {"message": "moderator", "role": user.role}

@app.get("/test/admin")
async def admin_endpoint(user: User = Depends(requires_admin)):
    return {"message": "admin", "role": user.role}

@app.post("/test/content")
async def content_endpoint():
    return {"message": "content"}

# Test client
client = TestClient(app)

def test_security_headers():
    """Test security headers are added to responses."""
    response = client.get("/test/public")
    assert response.status_code == 200
    
    # Check security headers
    headers = response.headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["X-XSS-Protection"] == "1; mode=block"
    assert "Content-Security-Policy" in headers
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

def test_rbac_public_endpoint():
    """Test public endpoint access."""
    response = client.get("/test/public")
    assert response.status_code == 200
    assert response.json() == {"message": "public"}

def test_rbac_protected_endpoints_unauthorized():
    """Test protected endpoints without authentication."""
    endpoints = ["/test/user", "/test/moderator", "/test/admin"]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401
        assert "detail" in response.json()

def test_rbac_user_access():
    """Test user role access."""
    # Mock user token
    app.dependency_overrides[get_current_user] = lambda: User(
        username="test_user",
        role="user"
    )
    
    # User can access user endpoint
    response = client.get("/test/user")
    assert response.status_code == 200
    assert response.json() == {"message": "user", "role": "user"}
    
    # User cannot access moderator endpoint
    response = client.get("/test/moderator")
    assert response.status_code == 403
    
    # User cannot access admin endpoint
    response = client.get("/test/admin")
    assert response.status_code == 403
    
    # Clean up
    app.dependency_overrides.clear()

def test_rbac_moderator_access():
    """Test moderator role access."""
    # Mock moderator token
    app.dependency_overrides[get_current_user] = lambda: User(
        username="test_moderator",
        role="moderator"
    )
    
    # Moderator can access user endpoint
    response = client.get("/test/user")
    assert response.status_code == 200
    assert response.json() == {"message": "user", "role": "moderator"}
    
    # Moderator can access moderator endpoint
    response = client.get("/test/moderator")
    assert response.status_code == 200
    assert response.json() == {"message": "moderator", "role": "moderator"}
    
    # Moderator cannot access admin endpoint
    response = client.get("/test/admin")
    assert response.status_code == 403
    
    # Clean up
    app.dependency_overrides.clear()

def test_rbac_admin_access():
    """Test admin role access."""
    # Mock admin token
    app.dependency_overrides[get_current_user] = lambda: User(
        username="test_admin",
        role="admin"
    )
    
    # Admin can access all endpoints
    endpoints = [
        ("/test/user", "user"),
        ("/test/moderator", "moderator"),
        ("/test/admin", "admin")
    ]
    for endpoint, message in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.json() == {"message": message, "role": "admin"}
    
    # Clean up
    app.dependency_overrides.clear()

def test_request_validation():
    """Test request validation middleware."""
    # Test content length limit
    large_content = "x" * (10 * 1024 * 1024 + 1)  # Exceeds 10MB
    response = client.post("/test/content", json={"content": large_content})
    assert response.status_code == 413
    
    # Test content type validation
    response = client.post(
        "/test/content",
        headers={"Content-Type": "text/plain"},
        data="invalid"
    )
    assert response.status_code == 415
    
    # Test valid request
    response = client.post("/test/content", json={"content": "valid"})
    assert response.status_code == 200 