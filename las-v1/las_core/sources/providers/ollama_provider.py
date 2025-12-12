"""
Ollama Provider - Supports both local and cloud models.

Supports:
- Local Ollama server (http://localhost:11434)
- Ollama Cloud API (https://ollama.com)
- Streaming and non-streaming responses
- Full LangChain integration
"""

import os
from typing import List, Dict, Any, Optional, Iterator
from sources.providers.base_provider import BaseProvider, ProviderConfig
from sources.logger import Logger

logger = Logger("ollama_provider.log")


class OllamaProvider(BaseProvider):
    """
    Ollama provider supporting both local and cloud models.
    
    Local models: llama3, gemma3, etc.
    Cloud models: gpt-oss:20b-cloud, gpt-oss:120b-cloud, qwen3-vl:235b-cloud, etc.
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        
        # Determine if using cloud or local
        self.is_cloud = self._is_cloud_model(config.model)
        
        if self.is_cloud:
            # Cloud configuration
            self.host = "https://ollama.com"
            self.api_key = os.getenv("OLLAMA_API_KEY") or os.getenv("OLLAMA_CLOUD_API_KEY")
            if not self.api_key:
                logger.warning("OLLAMA_API_KEY not set for cloud model. Cloud requests will fail.")
        else:
            # Local configuration
            self.host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
            self.api_key = None
        
        logger.info(f"Ollama Provider initialized: {'Cloud' if self.is_cloud else 'Local'} - {config.model}")
    
    def _is_cloud_model(self, model: str) -> bool:
        """Check if model is a cloud model."""
        cloud_suffixes = ["-cloud", ":cloud"]
        return any(model.endswith(suffix) or suffix in model for suffix in cloud_suffixes)
    
    def get_langchain_llm(self):
        """Get LangChain ChatOllama instance."""
        try:
            from langchain_ollama import ChatOllama
            
            kwargs = {
                "model": self.config.model,
                "base_url": self.host,
                "temperature": self.config.temperature,
            }
            
            # Add API key for cloud models
            if self.is_cloud and self.api_key:
                # LangChain Ollama doesn't directly support headers,
                # so we use the client_kwargs parameter
                kwargs["client_kwargs"] = {
                    "headers": {
                        "Authorization": f"Bearer {self.api_key}"
                    }
                }
            
            llm = ChatOllama(**kwargs)
            logger.info(f"Created LangChain ChatOllama: {self.config.model}")
            return llm
            
        except ImportError:
            logger.error("langchain-ollama not installed. Install with: pip install langchain-ollama")
            raise
        except Exception as e:
            logger.error(f"Failed to create ChatOllama: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate chat completion using Ollama Python SDK.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Response dict or generator if streaming
        """
        try:
            from ollama import Client
            
            # Create client
            client_kwargs = {"host": self.host}
            if self.is_cloud and self.api_key:
                client_kwargs["headers"] = {"Authorization": f"Bearer {self.api_key}"}
            
            client = Client(**client_kwargs)
            
            # Prepare options
            options = {}
            if "temperature" in kwargs:
                options["temperature"] = kwargs["temperature"]
            elif self.config.temperature is not None:
                options["temperature"] = self.config.temperature
            
            if "max_tokens" in kwargs:
                options["num_predict"] = kwargs["max_tokens"]
            elif self.config.max_tokens:
                options["num_predict"] = self.config.max_tokens
            
            # Make request
            response = client.chat(
                model=self.config.model,
                messages=messages,
                stream=stream,
                options=options if options else None
            )
            
            if stream:
                return self._stream_response(response)
            else:
                return response
                
        except Exception as e:
            logger.error(f"Ollama chat completion failed: {e}")
            raise
    
    def _stream_response(self, response) -> Iterator[Dict[str, Any]]:
        """Stream response chunks."""
        for chunk in response:
            yield {
                "content": chunk.get("message", {}).get("content", ""),
                "done": chunk.get("done", False),
                "model": chunk.get("model", self.config.model)
            }
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            from ollama import Client
            
            client_kwargs = {"host": self.host}
            if self.is_cloud and self.api_key:
                client_kwargs["headers"] = {"Authorization": f"Bearer {self.api_key}"}
            
            client = Client(**client_kwargs)
            models_response = client.list()
            
            # Extract model names
            models = []
            if hasattr(models_response, "models"):
                models = [model.model for model in models_response.models]
            elif isinstance(models_response, dict) and "models" in models_response:
                models = [model["name"] for model in models_response["models"]]
            
            logger.info(f"Listed {len(models)} Ollama models")
            return models
            
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []
    
    def supports_streaming(self) -> bool:
        """Ollama supports streaming."""
        return True
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "ollama"
