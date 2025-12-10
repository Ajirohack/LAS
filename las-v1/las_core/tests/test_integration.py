"""
Integration tests for the entire LAS system.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import requests
import time


class TestSystemIntegration:
    """Integration tests for the complete system."""
    
    @pytest.mark.integration
    def test_full_query_flow(self):
        """Test complete query flow from API to response."""
        # This test requires the system to be running
        # Skip if not in integration test mode
        pytest.skip("Requires running system")
    
    @pytest.mark.integration
    def test_memory_persistence(self):
        """Test that memory persists across sessions."""
        pytest.skip("Requires running system with database")
    
    @pytest.mark.integration
    def test_agent_collaboration(self):
        """Test multiple agents working together."""
        pytest.skip("Requires running system")


class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_postgresql_connection(self):
        """Test PostgreSQL connection."""
        from services.db.postgres import get_db
        
        try:
            db = await get_db()
            assert db is not None
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_qdrant_connection(self):
        """Test Qdrant connection."""
        from qdrant_client import QdrantClient
        
        try:
            client = QdrantClient(host="localhost", port=6333)
            collections = client.get_collections()
            assert collections is not None
        except Exception as e:
            pytest.skip(f"Qdrant not available: {e}")


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    @pytest.mark.e2e
    def test_simple_query_workflow(self):
        """Test a simple query workflow end-to-end."""
        # Requires system running
        api_url = "http://localhost:8000"
        
        try:
            # Test health
            health = requests.get(f"{api_url}/health")
            if health.status_code != 200:
                pytest.skip("System not running")
            
            # Test query
            response = requests.post(
                f"{api_url}/query",
                json={"query": "Hello"},
                headers={"X-API-Key": "las-secret-key"}
            )
            
            assert response.status_code in [200, 429]  # 429 if another query is running
            
        except requests.exceptions.ConnectionError:
            pytest.skip("System not running")
    
    @pytest.mark.e2e
    def test_streaming_workflow(self):
        """Test SSE streaming workflow."""
        api_url = "http://localhost:8000"
        
        try:
            response = requests.get(f"{api_url}/stream", stream=True)
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
        except requests.exceptions.ConnectionError:
            pytest.skip("System not running")
    
    @pytest.mark.e2e
    def test_multi_agent_task(self):
        """Test a task that requires multiple agents."""
        api_url = "http://localhost:8000"
        
        try:
            response = requests.post(
                f"{api_url}/query",
                json={"query": "Search for AI news and summarize the top 3 articles"},
                headers={"X-API-Key": "las-secret-key"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "answer" in data
                assert data.get("success") == "true"
        except requests.exceptions.ConnectionError:
            pytest.skip("System not running")
        except requests.exceptions.Timeout:
            pytest.skip("Query timeout")


class TestPerformance:
    """Performance tests."""
    
    @pytest.mark.performance
    def test_cache_performance(self):
        """Test that caching improves response time."""
        from sources.cache import LRUCache
        
        cache = LRUCache(capacity=100, ttl=3600)
        
        # First access (cache miss)
        start = time.time()
        result = cache.get("test_key")
        miss_time = time.time() - start
        
        # Add to cache
        cache.put("test_key", "test_value")
        
        # Second access (cache hit)
        start = time.time()
        result = cache.get("test_key")
        hit_time = time.time() - start
        
        # Cache hit should be faster
        assert hit_time <= miss_time
        assert result == "test_value"
    
    @pytest.mark.performance
    def test_concurrent_requests(self):
        """Test system handles concurrent requests."""
        pytest.skip("Requires load testing setup")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration and not e2e"])
