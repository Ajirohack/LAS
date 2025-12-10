"""
Test suite for authentication system.
"""

import pytest
from fastapi.testclient import TestClient
from database.models import Base, engine, User
from services.auth_service import get_auth_service
from sqlalchemy.orm import Session

@pytest.fixture(scope="module")
def test_client():
    """Create test client."""
    from api import app
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_service():
    """Get auth service instance."""
    return get_auth_service()

class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, test_client):
        """Test user registration."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"
        assert "id" in data
    
    def test_register_duplicate_user(self, test_client):
        """Test registration with duplicate username."""
        # First registration
        test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate",
                "email": "dup1@example.com",
                "password": "testpass123"
            }
        )
        
        # Duplicate registration
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate",
                "email": "dup2@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_weak_password(self, test_client):
        """Test registration with weak password."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "123"
            }
        )
        
        assert response.status_code == 400
        assert "at least 8 characters" in response.json()["detail"].lower()
    
    def test_login_success(self, test_client):
        """Test successful login."""
        # Register user first
        test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "testpass123"
            }
        )
        
        # Login
        response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": "loginuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_client):
        """Test login with wrong password."""
        response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": "loginuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, test_client):
        """Test login with non-existent user."""
        response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": "nonexistent",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_client):
        """Test getting current user info."""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "currentuser",
                "email": "current@example.com",
                "password": "testpass123"
            }
        )
        
        login_response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": "currentuser",
                "password": "testpass123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Get current user
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"
        assert data["email"] == "current@example.com"
    
    def test_protected_endpoint_without_token(self, test_client):
        """Test accessing protected endpoint without token."""
        response = test_client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No authorization header
    
    def test_protected_endpoint_invalid_token(self, test_client):
        """Test accessing protected endpoint with invalid token."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_refresh_token(self, test_client):
        """Test token refresh."""
        # Register and login
        test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "refreshuser",
                "email": "refresh@example.com",
                "password": "testpass123"
            }
        )
        
        login_response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": "refreshuser",
                "password": "testpass123"
            }
        )
        
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = test_client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

class TestPasswordHashing:
    """Test password hashing functionality."""
    
    def test_password_hashing(self, auth_service):
        """Test password is hashed correctly."""
        password = "mypassword123"
        hashed = auth_service.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 20
    
    def test_password_verification(self, auth_service):
        """Test password verification."""
        password = "mypassword123"
        hashed = auth_service.get_password_hash(password)
        
        assert auth_service.verify_password(password, hashed) is True
        assert auth_service.verify_password("wrongpassword", hashed) is False

class TestJWTTokens:
    """Test JWT token generation and validation."""
    
    def test_access_token_creation(self, auth_service):
        """Test access token creation."""
        token = auth_service.create_access_token(
            data={"sub": 1, "username": "test", "role": "user"}
        )
        
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_token_verification(self, auth_service):
        """Test token verification."""
        token = auth_service.create_access_token(
            data={"sub": 1, "username": "test", "role": "user"}
        )
        
        payload = auth_service.verify_token(token, token_type="access")
        
        assert payload is not None
        assert payload["sub"] == 1
        assert payload["username"] == "test"
        assert payload["role"] == "user"
    
    def test_invalid_token_verification(self, auth_service):
        """Test invalid token returns None."""
        payload = auth_service.verify_token("invalid_token", token_type="access")
        
        assert payload is None
    
    def test_token_blacklist(self, auth_service):
        """Test token blacklist functionality."""
        token = auth_service.create_access_token(
            data={"sub": 1, "username": "test", "role": "user"}
        )
        
        # Verify token works
        payload = auth_service.verify_token(token, token_type="access")
        assert payload is not None
        
        # Blacklist token
        auth_service.blacklist_token(token)
        
        # Verify token is now invalid
        payload = auth_service.verify_token(token, token_type="access")
        assert payload is None
