"""
OpenRouter Provider - Access 100+ AI models through a unified API.

Supports:
- All OpenRouter models (GPT-4, Claude, Gemini, Llama, etc.)
- Free models: google/gemma-2-27b-it:free, meta-llama/llama-3.2-3b-instruct:free
- Streaming and non-streaming responses
- Full LangChain integration via OpenAI compatibility
"""

import os
from typing import List, Dict, Any, Optional, Iterator
from sources.providers.base_provider import BaseProvider, ProviderConfig
from sources.logger import Logger

logger = Logger("openrouter_provider.log")


class OpenRouterProvider(BaseProvider):
    """
    OpenRouter provider with access to 100+ AI models.
    
    Uses OpenAI-compatible API with custom base URL.
    Free models available: google/gemma-2-27b-it:free, meta-llama/llama-3.2-3b-instruct:free
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set. Requests will fail.")
        
        # OpenRouter-specific headers
        self.app_name = os.getenv("APP_NAME", "Local Agent System")
        self.app_url = os.getenv("APP_URL", "https://github.com/your-repo/las")
        
        logger.info(f"OpenRouter Provider initialized: {config.model}")
    
    def get_langchain_llm(self):
        """Get LangChain ChatOpenAI instance configured for OpenRouter."""
        try:
            from langchain_openai import ChatOpenAI
            
            # OpenRouter uses OpenAI-compatible API
            llm = ChatOpenAI(
                model=self.config.model,
                openai_api_key=self.api_key,
                openai_api_base=self.base_url,
                temperature=self.config.temperature or 0.7,
                max_tokens=self.config.max_tokens,
                model_kwargs={
                    "extra_headers": {
                        "HTTP-Referer": self.app_url,
                        "X-Title": self.app_name,
                    }
                }
            )
            
            logger.info(f"Created LangChain ChatOpenAI for OpenRouter: {self.config.model}")
            return llm
            
        except ImportError:
            logger.error("langchain-openai not installed. Install with: pip install langchain-openai")
            raise
        except Exception as e:
            logger.error(f"Failed to create OpenRouter LLM: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate chat completion using OpenRouter API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Response dict or generator if streaming
        """
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.app_url,
                "X-Title": self.app_name,
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "stream": stream,
            }
            
            # Add optional parameters
            if "temperature" in kwargs:
                payload["temperature"] = kwargs["temperature"]
            elif self.config.temperature is not None:
                payload["temperature"] = self.config.temperature
            
            if "max_tokens" in kwargs:
                payload["max_tokens"] = kwargs["max_tokens"]
            elif self.config.max_tokens:
                payload["max_tokens"] = self.config.max_tokens
            
            # Make request
            with httpx.Client() as client:
                if stream:
                    with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    ) as response:
                        response.raise_for_status()
                        return self._stream_response(response)
                else:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    response.raise_for_status()
                    return response.json()
                    
        except Exception as e:
            logger.error(f"OpenRouter chat completion failed: {e}")
            raise
    
    def _stream_response(self, response) -> Iterator[Dict[str, Any]]:
        """Stream response chunks."""
        import json
        
        for line in response.iter_lines():
            if line.startswith("data: "):
                data = line[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield {
                                "content": content,
                                "done": chunk["choices"][0].get("finish_reason") is not None,
                                "model": chunk.get("model", self.config.model)
                            }
                except json.JSONDecodeError:
                    continue
    
    def list_models(self) -> List[str]:
        """List available OpenRouter models."""
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            
            with httpx.Client() as client:
                response = client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                models = []
                if "data" in data:
                    models = [model["id"] for model in data["data"]]
                
                logger.info(f"Listed {len(models)} OpenRouter models")
                return models
                
        except Exception as e:
            logger.error(f"Failed to list OpenRouter models: {e}")
            # Return some known free models as fallback
            return [
                "google/gemma-2-27b-it:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                "mistralai/mistral-7b-instruct:free",
                "google/gemini-flash-1.5:free"
            ]
    
    def supports_streaming(self) -> bool:
        """OpenRouter supports streaming."""
        return True
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "openrouter"
    
    @staticmethod
    def get_free_models() -> List[str]:
        """Get list of free models on OpenRouter."""
        return [
            "google/gemma-3-27b-it:free",
            "google/gemma-2-27b-it:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "meta-llama/llama-3.2-1b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "google/gemini-flash-1.5:free",
            "nousresearch/hermes-3-llama-3.1-405b:free",
            "microsoft/phi-3-medium-128k-instruct:free"
        ]
