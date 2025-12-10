"""
Simplified LLM Provider Wrapper - Backward compatible interface.

This module provides a backward-compatible wrapper around the new modular
provider architecture. The old 767-line Provider class now delegates to
the new provider factory while maintaining the same public interface.
"""

from typing import List, Dict, Any, Optional
from sources.provider_factory import ProviderFactory
from sources.providers.base_provider import BaseProvider
from sources.logger import Logger

class Provider:
    """
    Unified LLM provider interface (Backward Compatible).
    
    This class maintains the same interface as the old Provider class
    but uses the new modular provider architecture internally.
    """
    
    def __init__(
        self,
        provider_name: str,
        model: str,
        server_address: str = "127.0.0.1:5000",
        is_local: bool = False
    ):
        """
        Initialize provider.
        
        Args:
            provider_name: Provider name (ollama, openrouter, etc.)
            model: Model identifier
            server_address: Server address (legacy parameter)
            is_local: Whether provider is local (legacy parameter)
        """
        self.provider_name = provider_name.lower()
        self.model = model
        self.is_local = is_local
        self.server_address = server_address
        self.logger = Logger("provider.log")
        
        # Try to create using new provider system
        try:
            self._provider: Optional[BaseProvider] = ProviderFactory.create(
                provider_name=self.provider_name,
                model=self.model
            )
            self._using_new_provider = True
            self.logger.info(f"Using new provider architecture for {self.provider_name}")
        except ValueError:
            # Provider not yet migrated, will use legacy methods
            self._provider = None
            self._using_new_provider = False
            self.logger.info(f"Using legacy provider implementation for {self.provider_name}")
    
    def get_langchain_llm(self):
        """Get LangChain LLM instance."""
        if self._using_new_provider:
            return self._provider.get_langchain_llm()
        else:
            # Fall back to legacy implementation
            return self._get_legacy_langchain_llm()
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ):
        """Generate chat completion."""
        if self._using_new_provider:
            return self._provider.chat_completion(messages, stream, **kwargs)
        else:
            # Fall back to legacy implementation
            return self._legacy_chat_completion(messages, stream, **kwargs)
    
    def list_models(self, provider_name: Optional[str] = None) -> List[str]:
        """List available models."""
        if self._using_new_provider:
            return self._provider.list_models()
        else:
            # Fall back to legacy implementation
            return self._legacy_list_models()
    
    # Legacy implementation methods (to be removed after full migration)
    def _get_legacy_langchain_llm(self):
        """Legacy LangChain LLM creation (temporary)."""
        # Import legacy implementation if needed
        from sources.llm_provider_legacy import Provider as LegacyProvider
        legacy = LegacyProvider(self.provider_name, self.model)
        return legacy.get_langchain_llm()
    
    def _legacy_chat_completion(self, messages, stream=False, **kwargs):
        """Legacy chat completion (temporary)."""
        from sources.llm_provider_legacy import Provider as LegacyProvider
        legacy = LegacyProvider(self.provider_name, self.model)
        return legacy.chat_completion(messages, stream, **kwargs)
    
    def _legacy_list_models(self):
        """Legacy model listing (temporary)."""
        from sources.llm_provider_legacy import Provider as LegacyProvider
        legacy = LegacyProvider(self.provider_name, self.model)
        return legacy.list_models()
    
    # Utility methods for backward compatibility
    @property
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        if self._using_new_provider:
            return self._provider.supports_streaming()
        return True  # Assume true for legacy
    
    def __repr__(self) -> str:
        mode = "new" if self._using_new_provider else "legacy"
        return f"Provider({self.provider_name}, {self.model}, mode={mode})"

    def get_model_name(self) -> str:
        return self.model
