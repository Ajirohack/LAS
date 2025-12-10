"""
Connection Pool Service - Manages HTTP connection pools for external APIs.
"""

import httpx
from typing import Dict, Optional
from contextlib import asynccontextmanager
import asyncio

class ConnectionPool:
    """
    Manage HTTP connection pools for efficient API requests.
    
    This service maintains persistent HTTP connections to external APIs,
    reducing latency and improving throughput by reusing connections.
    """
    
    _instance: Optional['ConnectionPool'] = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        """Initialize connection pool manager."""
        self.pools: Dict[str, httpx.AsyncClient] = {}
        self.sync_pools: Dict[str, httpx.Client] = {}
    
    @classmethod
    async def get_instance(cls) -> 'ConnectionPool':
        """Get or create singleton instance."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = ConnectionPool()
        return cls._instance
    
    def get_client(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        **kwargs
    ) -> httpx.AsyncClient:
        """
        Get or create async HTTP client with connection pooling.
        
        Args:
            base_url: Base URL for the client
            headers: Optional default headers
            timeout: Request timeout in seconds
            **kwargs: Additional httpx.AsyncClient arguments
            
        Returns:
            Configured AsyncClient instance
        """
        if base_url not in self.pools:
            self.pools[base_url] = httpx.AsyncClient(
                base_url=base_url,
                headers=headers or {},
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                ),
                timeout=timeout,
                **kwargs
            )
        return self.pools[base_url]
    
    def get_sync_client(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        **kwargs
    ) -> httpx.Client:
        """
        Get or create sync HTTP client with connection pooling.
        
        Args:
            base_url: Base URL for the client
            headers: Optional default headers
            timeout: Request timeout in seconds
            **kwargs: Additional httpx.Client arguments
            
        Returns:
            Configured Client instance
        """
        if base_url not in self.sync_pools:
            self.sync_pools[base_url] = httpx.Client(
                base_url=base_url,
                headers=headers or {},
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                    keepalive_expiry=30.0
                ),
                timeout=timeout,
                **kwargs
            )
        return self.sync_pools[base_url]
    
    async def close_all(self):
        """Close all connection pools."""
        for client in self.pools.values():
            await client.aclose()
        
        for client in self.sync_pools.values():
            client.close()
        
        self.pools.clear()
        self.sync_pools.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        # Close sync clients
        for client in self.sync_pools.values():
            try:
                client.close()
            except:
                pass

# Singleton accessor
_pool_instance: Optional[ConnectionPool] = None

def get_connection_pool() -> ConnectionPool:
    """Get connection pool singleton (sync accessor)."""
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = ConnectionPool()
    return _pool_instance
