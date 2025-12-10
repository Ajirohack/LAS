import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from config.settings import settings
from sources.logger import Logger
import uuid

logger = Logger("rag_service.log")

class RAGService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        self.embeddings = OllamaEmbeddings(
            base_url=settings.provider_server_address,
            model="nomic-embed-text" # Or configurable via settings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        logger.info(f"RAG Service initialized. Connected to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")

    def create_collection(self, collection_name: str, vector_size: int = 768):
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE)
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            if "already exists" not in str(e):
                logger.error(f"Error creating collection: {e}")
                raise e

    def ingest_text(self, text: str, collection_name: str, metadata: Dict[str, Any] = None):
        try:
            # 1. Split text
            docs = [Document(page_content=text, metadata=metadata or {})]
            chunks = self.text_splitter.split_documents(docs)
            
            # 2. Embed chunks
            texts = [chunk.page_content for chunk in chunks]
            embeddings = self.embeddings.embed_documents(texts)
            
            # 3. Upload to Qdrant
            points = []
            for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
                points.append(models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "text": chunk.page_content,
                        "metadata": chunk.metadata
                    }
                ))
            
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Ingested {len(points)} chunks into {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error ingesting text: {e}")
            return False

    def search(self, query: str, collection_name: str, limit: int = 4):
        try:
            query_vector = self.embeddings.embed_query(query)
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            return [
                {
                    "text": hit.payload.get("text"),
                    "metadata": hit.payload.get("metadata"),
                    "score": hit.score
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

def get_rag_service():
    return RAGService()
