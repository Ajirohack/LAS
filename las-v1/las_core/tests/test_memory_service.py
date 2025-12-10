"""
Unit tests for Memory Service and 4-Tier Memory System.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.memory_service import MemoryService
from datetime import datetime


class TestMemoryService:
    """Test the Memory Service."""
    
    @pytest.fixture
    def memory_service(self):
        """Create a memory service instance for testing."""
        with patch('services.memory_service.get_db'):
            service = MemoryService()
            return service
    
    def test_memory_service_initialization(self, memory_service):
        """Test memory service initializes correctly."""
        assert memory_service is not None
    
    @pytest.mark.asyncio
    async def test_add_episodic_memory(self, memory_service):
        """Test adding episodic memory."""
        with patch.object(memory_service, 'db') as mock_db:
            mock_db.execute = AsyncMock()
            
            await memory_service.add_episodic_memory(
                session_id="test-session",
                user_input="What is AI?",
                agent_response="AI is artificial intelligence",
                context={"agent": "Planner"}
            )
            
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_semantic_memory(self, memory_service):
        """Test adding semantic memory."""
        with patch.object(memory_service, 'db') as mock_db:
            mock_db.execute = AsyncMock()
            
            await memory_service.add_semantic_memory(
                session_id="test-session",
                content="Python is a programming language",
                embedding=[0.1, 0.2, 0.3]
            )
            
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_entity_memory(self, memory_service):
        """Test adding entity memory."""
        with patch.object(memory_service, 'db') as mock_db:
            mock_db.execute = AsyncMock()
            
            await memory_service.add_entity_memory(
                session_id="test-session",
                entity_name="Python",
                entity_type="programming_language",
                attributes={"paradigm": "multi-paradigm", "typing": "dynamic"}
            )
            
            mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_episodic_memory(self, memory_service):
        """Test retrieving episodic memory."""
        with patch.object(memory_service, 'db') as mock_db:
            mock_result = Mock()
            mock_result.fetchall = AsyncMock(return_value=[
                {
                    "id": 1,
                    "session_id": "test-session",
                    "user_input": "Hello",
                    "agent_response": "Hi there",
                    "timestamp": datetime.now()
                }
            ])
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            memories = await memory_service.get_episodic_memory("test-session", limit=10)
            
            assert len(memories) == 1
            assert memories[0]["user_input"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_search_semantic_memory(self, memory_service):
        """Test searching semantic memory."""
        with patch.object(memory_service, 'qdrant_client') as mock_qdrant:
            mock_qdrant.search = AsyncMock(return_value=[
                Mock(payload={"content": "AI is artificial intelligence"}, score=0.95)
            ])
            
            results = await memory_service.search_semantic_memory(
                query_embedding=[0.1, 0.2, 0.3],
                limit=5
            )
            
            assert len(results) > 0
            assert results[0]["content"] == "AI is artificial intelligence"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
