"""
Local-Only Mode Enforcer - Ensure no external API calls.
"""

from typing import Set, Optional
import os

class LocalOnlyEnforcer:
    """
    Enforce local-only mode to prevent external API calls.
    
    Blocks all non-local LLM providers and network requests.
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        
        # Local-only providers
        self.local_providers: Set[str] = {"ollama", "llama_cpp"}
        
        # Blocked providers (require external APIs)
        self.external_providers: Set[str] = {
            "openai", "anthropic", "openrouter", 
            "groq", "gemini", "ollama-cloud"
        }
    
    def enable(self):
        """Enable local-only mode."""
        self.enabled = True
        os.environ["LAS_LOCAL_ONLY"] = "true"
    
    def disable(self):
        """Disable local-only mode."""
        self.enabled = False
        os.environ.pop("LAS_LOCAL_ONLY", None)
    
    def is_provider_allowed(self, provider: str) -> bool:
        """Check if provider is allowed in current mode."""
        if not self.enabled:
            return True  # All providers allowed when disabled
        
        return provider in self.local_providers
    
    def validate_network_request(self, url: str) -> bool:
        """
        Validate if network request is allowed.
        
        In local-only mode, only localhost requests allowed.
        """
        if not self.enabled:
            return True
        
        # Allow localhost and 127.0.0.1
        if "localhost" in url or "127.0.0.1" in url:
            return True
        
        return False

# Create singleton instance
_local_only_enforcer: Optional[LocalOnlyEnforcer] = None

def get_local_only_enforcer() -> LocalOnlyEnforcer:
    """Get or create LocalOnlyEnforcer instance."""
    global _local_only_enforcer
    if _local_only_enforcer is None:
        # Check environment variable
        enabled = os.getenv("LAS_LOCAL_ONLY", "false").lower() == "true"
        _local_only_enforcer = LocalOnlyEnforcer(enabled=enabled)
    return _local_only_enforcer
