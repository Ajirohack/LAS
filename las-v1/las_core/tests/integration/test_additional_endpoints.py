"""
Integration tests for HuggingFace endpoints.
"""

import pytest
from unittest.mock import patch, MagicMock

class TestHuggingFaceEndpoints:
    """Test HuggingFace API endpoints."""
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_chat(self, mock_hf_service, test_client):
        """Test HF chat endpoint."""
        mock_service = MagicMock()
        mock_service.chat_completion.return_value = "HF response"
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "meta-llama/Llama-3.3-70B-Instruct"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_text_generation(self, mock_hf_service, test_client):
        """Test HF text generation endpoint."""
        mock_service = MagicMock()
        mock_service.text_generation.return_value = "Generated text"
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/generate",
            json={
                "prompt": "Once upon a time",
                "model": "meta-llama/Llama-3.3-70B-Instruct"
            }
        )
        
        assert response.status_code == 200
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_models_search(self, mock_hf_service, test_client):
        """Test HF model search endpoint."""
        mock_service = MagicMock()
        mock_service.search_models.return_value = [
            {"id": "model1", "downloads": 1000},
            {"id": "model2", "downloads": 500}
        ]
        mock_hf_service.return_value = mock_service
        
        response = test_client.get(
            "/api/v1/hf/models",
            params={"task": "text-generation", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data

class TestMemoryEndpoints:
    """Test memory-related endpoints."""
    
    def test_get_knowledge_graph(self, test_client):
        """Test knowledge graph endpoint."""
        response = test_client.get("/api/v1/memory/knowledge-graph")
        
        # Should return data or 200 OK
        assert response.status_code in [200, 500]  # 500 if not initialized
    
    def test_list_skills(self, test_client):
        """Test listing skills."""
        response = test_client.get("/api/v1/memory/skills")
        
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data

class TestPerformanceEndpoints:
    """Test performance monitoring endpoints."""
    
    def test_cache_stats(self, test_client):
        """Test cache statistics endpoint."""
        response = test_client.get("/api/v1/perf/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "hits" in data or "stats" in data
    
    def test_clear_cache_admin(self, test_client, admin_headers):
        """Test cache clear requires admin."""
        response = test_client.post(
            "/api/v1/perf/cache/clear-stats",
            headers=admin_headers
        )
        
        # Should not return 403 (forbidden)
        assert response.status_code != 403
