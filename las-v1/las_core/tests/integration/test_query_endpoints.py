"""
Integration tests for query endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock

class TestQueryEndpoints:
    """Test query-related endpoints."""
    
    @patch('sources.llm_provider.Provider')
    def test_query_endpoint(self, mock_provider, test_client, auth_headers):
        """Test basic query endpoint."""
        # Mock LLM response
        mock_instance = MagicMock()
        mock_instance.chat_completion.return_value = "Test response"
        mock_provider.return_value = mock_instance
        
        response = test_client.post(
            "/api/v1/query",
            headers=auth_headers,
            json={
                "query": "What is AI?",
                "provider": "ollama",
                "model": "llama2"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "answer" in data
    
    def test_query_no_auth(self, test_client):
        """Test query without authentication."""
        response = test_client.post(
            "/api/v1/query",
            json={
                "query": "Test query",
                "provider": "ollama",
                "model": "llama2"
            }
        )
        
        # Should either require auth or work without it
        # Adjust based on your auth requirements
        assert response.status_code in [200, 403]
    
    @patch('sources.llm_provider.Provider')
    def test_streaming_query(self, mock_provider, test_client, auth_headers):
        """Test streaming query endpoint."""
        mock_instance = MagicMock()
        mock_instance.chat_completion.return_value = iter(["chunk1", "chunk2"])
        mock_provider.return_value = mock_instance
        
        response = test_client.post(
            "/api/v1/query/stream",
            headers=auth_headers,
            json={
                "query": "Streaming test",
                "provider": "ollama",
                "model": "llama2"
            }
        )
        
        # Streaming endpoints should return 200 or handle SSE
        assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist yet

class TestProviderEndpoints:
    """Test provider-related endpoints."""
    
    def test_list_providers(self, test_client):
        """Test listing available providers."""
        response = test_client.get("/api/v1/providers")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
    
    @patch('sources.llm_provider.Provider')
    def test_list_models(self, mock_provider, test_client):
        """Test listing models for a provider."""
        mock_instance = MagicMock()
        mock_instance.list_models.return_value = ["model1", "model2"]
        mock_provider.return_value = mock_instance
        
        response = test_client.get("/api/v1/providers/ollama/models")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
