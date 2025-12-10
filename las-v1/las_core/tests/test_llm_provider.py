"""
Test suite for LLM Provider.
"""

import pytest
from unittest.mock import Mock, patch
from sources.llm_provider import Provider

class TestLLMProvider:
    """Test LLM provider functionality."""
    
    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = Provider(provider_name="ollama", model="llama2")
        
        assert provider.provider_name == "ollama"
        assert provider.model == "llama2"
    
    @patch('sources.llm_provider.Ollama')
    def test_ollama_get_langchain_llm(self, mock_ollama):
        """Test Ollama LangChain LLM creation."""
        provider = Provider(provider_name="ollama", model="llama2")
        
        llm = provider.get_langchain_llm()
        
        mock_ollama.assert_called_once()
        assert llm is not None
    
    def test_list_models_ollama(self):
        """Test listing Ollama models."""
        with patch('sources.llm_provider.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "models": [
                    {"name": "llama2"},
                    {"name": "codellama"}
                ]
            }
            mock_get.return_value = mock_response
            
            provider = Provider(provider_name="ollama", model="llama2")
            models = provider.list_models()
            
            assert len(models) == 2
            assert "llama2" in models
            assert "codellama" in models
    
    @patch('sources.llm_provider.OpenAI')
    def test_openai_provider(self, mock_openai):
        """Test OpenAI provider initialization."""
        provider = Provider(provider_name="openai", model="gpt-4")
        
        llm = provider.get_langchain_llm()
        
        mock_openai.assert_called()
        assert llm is not None
    
    @patch('services.huggingface_service.get_huggingface_service')
    def test_huggingface_provider(self, mock_hf_service):
        """Test HuggingFace provider."""
        mock_service = Mock()
        mock_service.chat_completion.return_value = "Test response"
        mock_hf_service.return_value = mock_service
        
        provider = Provider(provider_name="huggingface", model="meta-llama/Llama-3.3-70B-Instruct")
        
        response = provider.huggingface_fn([{"role": "user", "content": "Test"}])
        
        assert response == "Test response"
    
    def test_invalid_provider(self):
        """Test invalid provider name."""
        provider = Provider(provider_name="invalid_provider", model="model")
        
        with pytest.raises(Exception):
            provider.get_langchain_llm()
