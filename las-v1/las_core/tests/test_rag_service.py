"""
Unit tests for RAG Service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.rag_service import RAGService


class TestRAGService:
    """Test the RAG Service."""
    
    @pytest.fixture
    def rag_service(self):
        """Create a RAG service instance for testing."""
        with patch('services.rag_service.QdrantClient'):
            service = RAGService()
            return service
    
    def test_rag_service_initialization(self, rag_service):
        """Test RAG service initializes correctly."""
        assert rag_service is not None
        assert rag_service.collection_name == "las_knowledge"
    
    @pytest.mark.asyncio
    async def test_add_document(self, rag_service):
        """Test adding a document to the knowledge base."""
        with patch.object(rag_service, 'client') as mock_client:
            mock_client.upsert = AsyncMock()
            
            await rag_service.add_document(
                doc_id="doc1",
                content="This is a test document",
                metadata={"source": "test"}
            )
            
            mock_client.upsert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_documents(self, rag_service):
        """Test searching documents."""
        with patch.object(rag_service, 'client') as mock_client:
            mock_client.search = AsyncMock(return_value=[
                Mock(
                    payload={"content": "Test document", "metadata": {"source": "test"}},
                    score=0.9
                )
            ])
            
            results = await rag_service.search(
                query="test query",
                limit=5
            )
            
            assert len(results) > 0
            assert results[0]["content"] == "Test document"
            assert results[0]["score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_delete_document(self, rag_service):
        """Test deleting a document."""
        with patch.object(rag_service, 'client') as mock_client:
            mock_client.delete = AsyncMock()
            
            await rag_service.delete_document("doc1")
            
            mock_client.delete.assert_called_once()
    
    def test_generate_embedding(self, rag_service):
        """Test embedding generation."""
        with patch.object(rag_service, 'embedding_model') as mock_model:
            mock_model.encode = Mock(return_value=[0.1, 0.2, 0.3])
            
            embedding = rag_service.generate_embedding("test text")
            
            assert len(embedding) == 3
            assert embedding == [0.1, 0.2, 0.3]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
