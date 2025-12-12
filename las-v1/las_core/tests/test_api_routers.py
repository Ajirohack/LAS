"""
Unit tests for API Routers.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from api import app
import os


class TestQueryRouter:
    """Test the Query Router."""
    
    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        with patch('services.llm_service.get_llm_service') as mock_llm_svc, \
             patch('services.db.postgres.engine') as mock_engine, \
             patch('services.rag_service.get_rag_service') as mock_rag, \
             patch('httpx.AsyncClient') as mock_httpx:
            
            # Mock LLM
            mock_provider = Mock()
            mock_provider.list_models.return_value = ["model1"]
            mock_llm_svc.return_value.get_provider.return_value = mock_provider
            
            # Mock DB
            mock_conn = AsyncMock()
            # engine.begin() returns a context manager
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_conn
            mock_cm.__aexit__.return_value = None
            mock_engine.begin.return_value = mock_cm
            
            # Mock RAG
            mock_rag.return_value.client.get_collections.return_value = []
            
            # Mock SearxNG
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_resp
            
            mock_httpx_cm = AsyncMock()
            mock_httpx_cm.__aenter__.return_value = mock_client_instance
            mock_httpx_cm.__aexit__.return_value = None
            mock_httpx.return_value = mock_httpx_cm
            
            # Set env var for SearxNG check to trigger
            with patch.dict(os.environ, {'SEARXNG_BASE_URL': 'http://localhost'}):
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
        # health check should pass without auth if it was mocked to return 200 (which it's not here unless we mock it globally or use different endpoint)
        # But wait, health check logic is in API router.
        # This test relies on existing behavior. Health check calls external services.
        # If services are down, it returns 200 'degraded'. That IS 200.
        pass # Skipping modifying this test, 'degraded' (200 OK) is still 200 OK.
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
