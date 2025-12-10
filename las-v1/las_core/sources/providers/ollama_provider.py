"""
Ollama Provider - Local LLM provider implementation.
"""

from typing import List, Dict, Iterator, Union
import requests
from langchain_community.llms import Ollama
from sources.providers.base_provider import BaseProvider, ProviderConfig

class OllamaProvider(BaseProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.base_url:
            self.base_url = "http://localhost:11434"
    
    @property
    def provider_name(self) -> str:
        return "ollama"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using Ollama API."""
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": stream,
                **kwargs
            }
            
            response = requests.post(url, json=payload, stream=stream)
            response.raise_for_status()
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.json()["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response from Ollama."""
        import json
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        content = chunk["message"].get("content", "")
                        if content:
                            yield content
                except json.JSONDecodeError:
                    continue
    
    def get_langchain_llm(self):
        """Get LangChain Ollama LLM instance."""
        return Ollama(
            model=self.model,
            base_url=self.base_url
        )
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except Exception as e:
            raise RuntimeError(f"Failed to list Ollama models: {e}")
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Ollama is free (local)."""
        return 0.0
