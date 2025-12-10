"""
Test suite for new provider architecture.
"""

import pytest
from sources.provider_factory import ProviderFactory
from sources.providers.base_provider import BaseProvider
from sources.llm_provider import Provider

class TestProviderFactory:
    """Test provider factory functionality."""
    
    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        provider = ProviderFactory.create(
            provider_name="ollama",
            model="llama2"
        )
        
        assert provider is not None
        assert provider.provider_name == "ollama"
        assert provider.model == "llama2"
    
    def test_create_openrouter_provider(self):
        """Test creating OpenRouter provider."""
        provider = ProviderFactory.create(
            provider_name="openrouter",
            model="openai/gpt-4-turbo",
            api_key="test_key"
        )
        
        assert provider is not None
        assert provider.provider_name == "openrouter"
        assert provider.model == "openai/gpt-4-turbo"
    
    def test_create_huggingface_provider(self):
        """Test creating HuggingFace provider."""
        provider = ProviderFactory.create(
            provider_name="huggingface",
            model="meta-llama/Llama-3.3-70B-Instruct"
        )
        
        assert provider is not None
        assert provider.provider_name == "huggingface"
    
    def test_invalid_provider(self):
        """Test creating invalid provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.create(
                provider_name="invalid_provider",
                model="model"
            )
        
        assert "Unknown provider" in str(exc_info.value)
    
    def test_list_providers(self):
        """Test listing registered providers."""
        providers = ProviderFactory.list_providers()
        
        assert "ollama" in providers
        assert "openrouter" in providers
        assert "huggingface" in providers

class TestBackwardCompatibility:
    """Test backward compatibility with legacy Provider interface."""
    
    def test_provider_wrapper_ollama(self):
        """Test Provider wrapper with Ollama."""
        provider = Provider(
            provider_name="ollama",
            model="llama2"
        )
        
        assert provider.provider_name == "ollama"
        assert provider.model == "llama2"
        assert provider._using_new_provider is True
    
    def test_provider_wrapper_openrouter(self):
        """Test Provider wrapper with OpenRouter."""
        provider = Provider(
            provider_name="openrouter",
            model="openai/gpt-4"
        )
        
        assert provider.provider_name == "openrouter"
        assert provider._using_new_provider is True
    
    def test_provider_supports_streaming(self):
        """Test streaming support check."""
        provider = Provider("ollama", "llama2")
        
        assert provider.supports_streaming is True
    
    def test_provider_repr(self):
        """Test provider string representation."""
        provider = Provider("ollama", "llama2")
        repr_str = repr(provider)
        
        assert "Ollama" in repr_str or "ollama" in repr_str
        assert "llama2" in repr_str

class TestProviderFunctionality:
    """Test actual provider functionality."""
    
    @pytest.mark.skip(reason="Requires local Ollama server")
    def test_ollama_list_models(self):
        """Test listing Ollama models."""
        provider = Provider("ollama", "llama2")
        models = provider.list_models()
        
        assert isinstance(models, list)
    
    def test_openrouter_list_models(self):
        """Test listing OpenRouter models."""
        provider = Provider("openrouter", "openai/gpt-4")
        models = provider.list_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
