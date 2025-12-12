from typing import Dict, Type, Optional, List
from sources.providers.base_provider import BaseProvider, ProviderConfig

class ProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _providers: Dict[str, str] = {
        # LiteLLM - Unified gateway to 100+ providers
        "litellm": "sources.providers.litellm_provider.LiteLLMProvider",
        
        # Individual providers (can also be accessed via LiteLLM)
        "ollama": "sources.providers.ollama_provider.OllamaProvider",
        "openrouter": "sources.providers.openrouter_provider.OpenRouterProvider",
        "huggingface": "sources.providers.huggingface_provider.HuggingFaceProvider",
        "openai": "sources.providers.openai_provider.OpenAIProvider",
        "gemini": "sources.providers.gemini_provider.GeminiProvider",
        "google": "sources.providers.gemini_provider.GeminiProvider",  # Alias
        "groq": "sources.providers.groq_provider.GroqProvider",
        "anthropic": "sources.providers.anthropic_provider.AnthropicProvider",
        "claude": "sources.providers.anthropic_provider.AnthropicProvider",  # Alias
        "deepseek": "sources.providers.deepseek_provider.DeepSeekProvider",
    }
    
    @classmethod
    def create(
        cls,
        provider_name: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ) -> BaseProvider:
        """
        Create provider instance.
        
        Args:
            provider_name: Name of the provider (ollama, openrouter, etc.)
            model: Model identifier
            api_key: Optional API key
            base_url: Optional base URL
            **kwargs: Additional provider-specific configuration
            
        Returns:
            BaseProvider instance
            
        Raises:
            ValueError: If provider_name is unknown
        """
        provider_name = provider_name.lower()
        provider_path = cls._providers.get(provider_name)
        
        if not provider_path:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider: '{provider_name}'. "
                f"Available providers: {available}"
            )
        module_name, class_name = provider_path.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        
        config = ProviderConfig(
            model=model,
            api_key=api_key,
            base_url=base_url,
            extra=kwargs
        )
        
        provider = provider_class(config)
        provider.validate_config()
        
        return provider
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseProvider]):
        """
        Register a custom provider.
        
        Args:
            name: Provider name
            provider_class: Provider class (must inherit from BaseProvider)
        """
        if not issubclass(provider_class, BaseProvider):
            raise TypeError(
                f"Provider class must inherit from BaseProvider, "
                f"got {provider_class.__name__}"
            )
        
        cls._providers[name.lower()] = f"{provider_class.__module__}.{provider_class.__name__}"
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """Get list of registered providers."""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_class(cls, name: str) -> Optional[Type[BaseProvider]]:
        """Get provider class by name."""
        provider_path = cls._providers.get(name.lower())
        if not provider_path:
            return None
        module_name, class_name = provider_path.rsplit('.', 1)
        import importlib
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
