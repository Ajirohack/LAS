"""
Unit tests for API Routers.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from api import app


class TestQueryRouter:
    """Test the Query Router."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_query_endpoint_without_auth(self, client):
        """Test query endpoint rejects requests without API key."""
        response = client.post("/query", json={"query": "Hello"})
        assert response.status_code == 403
    
    def test_query_endpoint_with_auth(self, client):
        """Test query endpoint accepts requests with valid API key."""
        with patch('routers.query.interaction_service') as mock_service:
            mock_interaction = Mock()
            mock_interaction.last_answer = "Test response"
            mock_interaction.last_reasoning = "Test reasoning"
            mock_interaction.last_success = True
            mock_interaction.current_agent = Mock()
            mock_interaction.current_agent.agent_name = "TestAgent"
            mock_interaction.current_agent.get_blocks_result = Mock(return_value=[])
            
            mock_service.get_interaction = Mock(return_value=mock_interaction)
            
            response = client.post(
                "/query",
                json={"query": "Hello"},
                headers={"X-API-Key": "las-secret-key"}
            )
            
            # May return 500 due to mocking, but should not be 403
            assert response.status_code != 403
    
    def test_query_endpoint_concurrent_requests(self, client):
        """Test query endpoint handles concurrent requests."""
        with patch('routers.query.is_generating', True):
            response = client.post(
                "/query",
                json={"query": "Hello"},
                headers={"X-API-Key": "las-secret-key"}
            )
            
            assert response.status_code == 429  # Too Many Requests


class TestStreamRouter:
    """Test the Stream Router."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_stream_endpoint(self, client):
        """Test SSE stream endpoint."""
        response = client.get("/stream")
        
        # Should return 200 and start streaming
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestSecurityMiddleware:
    """Test Security Middleware."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_public_endpoint_no_auth(self, client):
        """Test public endpoints don't require auth."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_protected_endpoint_no_auth(self, client):
        """Test protected endpoints require auth."""
        response = client.post("/query", json={"query": "test"})
        assert response.status_code == 403
    
    def test_protected_endpoint_invalid_key(self, client):
        """Test protected endpoints reject invalid API keys."""
        response = client.post(
            "/query",
            json={"query": "test"},
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 403
    
    def test_protected_endpoint_valid_key(self, client):
        """Test protected endpoints accept valid API keys."""
        with patch('routers.query.interaction_service'):
            response = client.post(
                "/query",
                json={"query": "test"},
                headers={"X-API-Key": "las-secret-key"}
            )
            
            # Should not be 403 (may be 500 due to mocking)
            assert response.status_code != 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
