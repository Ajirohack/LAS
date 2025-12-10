"""
Unit tests for LLM Service and Provider caching.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sources.llm_provider import Provider
from sources.cache import LRUCache
from services.llm_service import LLMService, get_llm_service


class TestLRUCache:
    """Test the LRU Cache implementation."""
    
    def test_cache_put_and_get(self):
        """Test basic put and get operations."""
        cache = LRUCache(capacity=2, ttl=3600)
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_with_list_key(self):
        """Test cache with unhashable list keys."""
        cache = LRUCache(capacity=2, ttl=3600)
        key = ["provider", "model", [{"role": "user", "content": "test"}]]
        cache.put(key, "response")
        assert cache.get(key) == "response"
    
    def test_cache_capacity_limit(self):
        """Test that cache respects capacity limit."""
        cache = LRUCache(capacity=2, ttl=3600)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
    
    def test_cache_ttl_expiration(self):
        """Test that cache entries expire after TTL."""
        import time
        cache = LRUCache(capacity=10, ttl=1)  # 1 second TTL
        cache.put("key1", "value1")
        
        assert cache.get("key1") == "value1"
        time.sleep(1.1)  # Wait for expiration
        assert cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test cache clear operation."""
        cache = LRUCache(capacity=10, ttl=3600)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestProvider:
    """Test the LLM Provider with caching."""
    
    @patch('sources.llm_provider.Logger')
    @patch('sources.llm_provider.pretty_print')
    def test_provider_initialization(self, mock_print, mock_logger):
        """Test provider initializes with cache."""
        provider = Provider("test", "test-model")
        assert provider.cache is not None
        assert provider.provider_name == "test"
        assert provider.model == "test-model"
    
    @patch('sources.llm_provider.Logger')
    @patch('sources.llm_provider.pretty_print')
    def test_provider_caching(self, mock_print, mock_logger):
        """Test that provider caches responses."""
        provider = Provider("test", "test-model")
        history = [{"role": "user", "content": "Hello"}]
        
        # First call should execute and cache
        response1 = provider.respond(history, verbose=False)
        
        # Second call should return cached result
        response2 = provider.respond(history, verbose=False)
        
        assert response1 == response2


class TestLLMService:
    """Test the LLM Service singleton."""
    
    @patch('services.llm_service.Provider')
    @patch('services.llm_service.settings')
    def test_llm_service_singleton(self, mock_settings, mock_provider):
        """Test that LLMService is a singleton."""
        mock_settings.provider_name = "test"
        mock_settings.provider_model = "test-model"
        mock_settings.provider_server_address = "localhost:8000"
        mock_settings.is_local = True
        
        service1 = get_llm_service()
        service2 = get_llm_service()
        
        assert service1 is service2
    
    @patch('services.llm_service.Provider')
    @patch('services.llm_service.settings')
    def test_llm_service_get_provider(self, mock_settings, mock_provider):
        """Test getting provider from service."""
        mock_settings.provider_name = "test"
        mock_settings.provider_model = "test-model"
        mock_settings.provider_server_address = "localhost:8000"
        mock_settings.is_local = True
        
        service = get_llm_service()
        provider = service.get_provider()
        
        assert provider is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
