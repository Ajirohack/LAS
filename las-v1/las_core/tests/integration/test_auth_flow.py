"""
Integration tests for authentication flow and endpoints.
"""

import pytest
from fastapi.testclient import TestClient

class TestAuthenticationFlow:
    """Test complete authentication flows."""
    
    def test_user_registration(self, test_client):
        """Test user registration endpoint."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
                "role": "user"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_duplicate_username(self, test_client, test_user):
        """Test registration with duplicate username fails."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user["username"],
                "email": "different@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 400
    
    def test_login_success(self, test_client, test_user):
        """Test successful login."""
        response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_client, test_user):
        """Test login with wrong password."""
        response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": test_user["username"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_client, auth_headers):
        """Test getting current user info."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "role" in data
    
    def test_protected_endpoint_no_auth(self, test_client):
        """Test accessing protected endpoint without auth."""
        response = test_client.get("/api/v1/auth/me")
        
        assert response.status_code == 403
    
    def test_token_refresh(self, test_client, test_user):
        """Test token refresh."""
        # Login
        login_response = test_client.post(
            "/api/v1/auth/login",
            params={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        tokens = login_response.json()
        
        # Refresh
        response = test_client.post(
            "/api/v1/auth/refresh",
            params={"refresh_token": tokens["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_logout(self, test_client, auth_token):
        """Test logout invalidates token."""
        response = test_client.post(
            "/api/v1/auth/logout",
            params={"access_token": auth_token}
        )
        
        assert response.status_code == 200
        
        # Try using token after logout
        me_response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert me_response.status_code == 401

class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def test_admin_only_endpoint(self, test_client, auth_headers):
        """Test user cannot access admin endpoint."""
        response = test_client.post(
            "/api/v1/perf/cache/clear-stats",
            headers=auth_headers
        )
        
        assert response.status_code == 403
    
    def test_admin_access(self, test_client, admin_headers):
        """Test admin can access admin endpoint."""
        response = test_client.post(
            "/api/v1/perf/cache/clear-stats",
            headers=admin_headers
        )
        
        # Should succeed (or return expected error, not 403)
        assert response.status_code != 403
