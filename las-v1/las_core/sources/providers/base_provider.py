"""
Base Provider Abstract Class for LLM integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Iterator, Union
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    stream: bool = False
    extra: Dict[str, Any] = None

class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider configuration
        """
        self.config = config
        self.model = config.model
        self.api_key = config.api_key
        self.base_url = config.base_url
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return provider name."""
        pass
    
    @abstractmethod
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Generate chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Complete response string or iterator of chunks
        """
        pass
    
    @abstractmethod
    def get_langchain_llm(self):
        """
        Get LangChain LLM instance for this provider.
        
        Returns:
            LangChain LLM object
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of model names/IDs
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate provider configuration.
        
        Returns:
            True if config is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        if not self.model:
            raise ValueError(f"{self.provider_name}: model is required")
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Total cost in USD
        """
        # Default: free/local
        return 0.0
    
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        return True
    
    def supports_function_calling(self) -> bool:
        """Check if provider supports function calling."""
        return False
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"
