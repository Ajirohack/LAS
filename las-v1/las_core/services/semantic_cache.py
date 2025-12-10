"""
Semantic Cache - Embedding-based caching for LLM responses.

Reduces costs and latency by serving cached responses for similar queries.
"""

import json
import hashlib
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

class SemanticCache:
    """
    Semantic caching using embeddings for similarity matching.
    Caches query-response pairs and retrieves similar queries.
    """
    
    def __init__(self, storage_dir: str = "data/cache", 
                 similarity_threshold: float = 0.85,
                 ttl_hours: int = 24):
        """
        Initialize semantic cache.
        
        Args:
            storage_dir: Directory for cache storage
            similarity_threshold: Minimum similarity for cache hit (0-1)
            ttl_hours: Time to live in hours
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.similarity_threshold = similarity_threshold
        self.ttl = timedelta(hours=ttl_hours)
        
        self.cache_file = self.storage_dir / "semantic_cache.json"
        self.cache: List[Dict[str, Any]] = []
        self.load_cache()
        
        # Stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0
        }
    
    def load_cache(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                self._cleanup_expired()
            except Exception as e:
                print(f"Failed to load cache: {e}")
                self.cache = []
    
    def save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")
    
    def _cleanup_expired(self):
        """Remove expired cache entries."""
        now = datetime.now()
        self.cache = [
            entry for entry in self.cache
            if datetime.fromisoformat(entry["expires_at"]) > now
        ]
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text.
        In production, use sentence-transformers or similar.
        For now, using a simple hash-based approach.
        """
        # TODO: Replace with actual embeddings (sentence-transformers, OpenAI, etc.)
        # This is a placeholder that creates a deterministic vector from text
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to numpy array (normalized)
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(float)
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get(self, query: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query.
        
        Args:
            query: Query text
            metadata: Optional metadata (provider, model, etc.)
        
        Returns:
            Cached response or None
        """
        self.stats["total_queries"] += 1
        self._cleanup_expired()
        
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Find similar cached queries
        best_match = None
        best_similarity = 0.0
        
        for entry in self.cache:
            # Check metadata match if provided
            if metadata:
                entry_metadata = entry.get("metadata", {})
                if entry_metadata.get("provider") != metadata.get("provider"):
                    continue
                if entry_metadata.get("model") != metadata.get("model"):
                    continue
            
            # Calculate similarity
            cached_embedding = np.array(entry["embedding"])
            similarity = self._cosine_similarity(query_embedding, cached_embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = entry
        
        # Check if similarity exceeds threshold
        if best_similarity >= self.similarity_threshold:
            self.stats["hits"] += 1
            return {
                "response": best_match["response"],
                "similarity": best_similarity,
                "cached_at": best_match["cached_at"],
                "original_query": best_match["query"]
            }
        
        self.stats["misses"] += 1
        return None
    
    def set(self, query: str, response: Any, metadata: Optional[Dict[str, Any]] = None):
        """
        Cache query-response pair.
        
        Args:
            query: Query text
            response: Response to cache
            metadata: Optional metadata
        """
        query_embedding = self._get_embedding(query)
        
        entry = {
            "query": query,
            "response": response,
            "embedding": query_embedding.tolist(),
            "metadata": metadata or {},
            "cached_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + self.ttl).isoformat()
        }
        
        self.cache.append(entry)
        self.save_cache()
    
    def invalidate(self, query: Optional[str] = None):
        """
        Invalidate cache entries.
        
        Args:
            query: Optional specific query to invalidate (invalidates all if None)
        """
        if query:
            query_embedding = self._get_embedding(query)
            self.cache = [
                entry for entry in self.cache
                if self._cosine_similarity(np.array(entry["embedding"]), query_embedding) < 0.95
            ]
        else:
            self.cache = []
        
        self.save_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        hit_rate = (self.stats["hits"] / self.stats["total_queries"] * 100
                   if self.stats["total_queries"] > 0 else 0)
        
        return {
            "total_queries": self.stats["total_queries"],
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": round(hit_rate, 2),
            "cache_size": len(self.cache)
        }
    
    def clear_stats(self):
        """Reset statistics."""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0
        }

# Create singleton instance
_semantic_cache: Optional[SemanticCache] = None

def get_semantic_cache() -> SemanticCache:
    """Get or create SemanticCache instance."""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = SemanticCache()
    return _semantic_cache
