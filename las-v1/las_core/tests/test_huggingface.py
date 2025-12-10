"""
Test suite for HuggingFace router.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

@pytest.fixture(scope="module")
def test_client():
    """Create test client."""
    from api import app
    client = TestClient(app)
    return client

class TestHuggingFaceRouter:
    """Test HuggingFace integration endpoints."""
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_chat(self, mock_hf_service, test_client):
        """Test chat completion endpoint."""
        # Mock service
        mock_service = Mock()
        mock_service.chat_completion.return_value = "Test response"
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "model": "meta-llama/Llama-3.3-70B-Instruct"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["response"] == "Test response"
        mock_service.chat_completion.assert_called_once()
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_generate(self, mock_hf_service, test_client):
        """Test text generation endpoint."""
        mock_service = Mock()
        mock_service.text_generation.return_value = "Generated text"
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/generate",
            json={
                "prompt": "Once upon a time",
                "model": "meta-llama/Llama-3.3-70B-Instruct",
                "max_new_tokens": 100
            }
        )
        
        assert response.status_code == 200
        assert response.json()["generated_text"] == "Generated text"
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_text_to_image(self, mock_hf_service, test_client):
        """Test image generation endpoint."""
        mock_service = Mock()
        mock_service.text_to_image.return_value = "/path/to/image.png"
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/text-to-image",
            json={
                "prompt": "A beautiful sunset",
                "model": "stabilityai/stable-diffusion-3.5-large"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["image_path"] == "/path/to/image.png"
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_embeddings(self, mock_hf_service, test_client):
        """Test embeddings generation endpoint."""
        mock_service = Mock()
        mock_service.feature_extraction.return_value = [[0.1, 0.2, 0.3]]
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/embeddings",
            json={
                "texts": ["Test text"],
                "model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        )
        
        assert response.status_code == 200
        assert "embeddings" in response.json()
        assert len(response.json()["embeddings"]) == 1
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_search_models(self, mock_hf_service, test_client):
        """Test model search endpoint."""
        mock_service = Mock()
        mock_service.search_models.return_value = [
            {"id": "model1", "task": "text-generation", "downloads": 1000},
            {"id": "model2", "task": "text-generation", "downloads": 500}
        ]
        mock_hf_service.return_value = mock_service
        
        response = test_client.get(
            "/api/v1/hf/models",
            params={"task": "text-generation", "limit": 10}
        )
        
        assert response.status_code == 200
        assert len(response.json()["models"]) == 2
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_hf_error_handling(self, mock_hf_service, test_client):
        """Test error handling in HF endpoints."""
        mock_service = Mock()
        mock_service.chat_completion.side_effect = RuntimeError("API Error")
        mock_hf_service.return_value = mock_service
        
        response = test_client.post(
            "/api/v1/hf/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        
        assert response.status_code == 500
        assert "API Error" in response.json()["detail"]
