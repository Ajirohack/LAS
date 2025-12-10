from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from services.db.postgres import engine, AsyncSessionLocal
from services.rag_service import get_rag_service
from sources.logger import Logger
import json

Base = declarative_base()
logger = Logger("memory_service.log")

# --- Database Models ---
class EpisodicMemory(Base):
    __tablename__ = "episodic_memory"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default={})

class EntityMemory(Base):
    __tablename__ = "entity_memory"
    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String, unique=True, index=True)
    entity_type = Column(String) # e.g., "user", "project", "tool"
    attributes = Column(JSON, default={})
    last_updated = Column(DateTime, default=datetime.utcnow)

# --- Memory Service ---
class MemoryService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.rag_service = get_rag_service()
        # Ensure Qdrant collection for long-term memory exists
        try:
            self.rag_service.create_collection("long_term_memory")
        except:
            pass # Collection might already exist

    async def add_episodic_memory(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Tier 1: Short-term / Episodic Memory (Session-based)"""
        async with AsyncSessionLocal() as session:
            memory = EpisodicMemory(
                session_id=session_id,
                role=role,
                content=content,
                metadata_=metadata or {}
            )
            session.add(memory)
            await session.commit()
            
            # Also add to Long-term memory (Tier 2) if significant
            # For now, we add everything to vector DB for semantic search
            self.rag_service.ingest_text(
                text=f"{role}: {content}",
                collection_name="long_term_memory",
                metadata={"session_id": session_id, "role": role, "timestamp": str(datetime.utcnow())}
            )

    async def get_episodic_memory(self, session_id: str, limit: int = 10):
        """Retrieve recent conversation history"""
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(EpisodicMemory)
                .where(EpisodicMemory.session_id == session_id)
                .order_by(EpisodicMemory.timestamp.desc())
                .limit(limit)
            )
            memories = result.scalars().all()
            return reversed(memories) # Return in chronological order

    async def search_long_term_memory(self, query: str, limit: int = 5):
        """Tier 2: Long-term Semantic Memory"""
        return self.rag_service.search(query, "long_term_memory", limit)

    async def update_entity_memory(self, name: str, entity_type: str, attributes: dict):
        """Tier 3: Entity Memory (Facts about users/projects)"""
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EntityMemory).where(EntityMemory.entity_name == name))
            entity = result.scalar_one_or_none()
            
            if entity:
                # Merge attributes
                current_attrs = entity.attributes or {}
                current_attrs.update(attributes)
                entity.attributes = current_attrs
                entity.last_updated = datetime.utcnow()
            else:
                entity = EntityMemory(
                    entity_name=name,
                    entity_type=entity_type,
                    attributes=attributes
                )
                session.add(entity)
            await session.commit()

    async def get_entity_memory(self, name: str):
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(EntityMemory).where(EntityMemory.entity_name == name))
            entity = result.scalar_one_or_none()
            return entity.attributes if entity else None

def get_memory_service():
    return MemoryService()
