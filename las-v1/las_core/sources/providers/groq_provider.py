"""
Groq Provider - Groq API implementation for fast inference.
"""

from typing import List, Dict, Iterator, Union
from groq import Groq
from sources.providers.base_provider import BaseProvider, ProviderConfig

class GroqProvider(BaseProvider):
    """Groq API provider for ultra-fast LLM inference."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.api_key:
            import os
            self.api_key = os.getenv("GROQ_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "groq"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using Groq API."""
        client = Groq(api_key=self.api_key)
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                **kwargs
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response."""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
    
    def get_langchain_llm(self):
        """Get LangChain Groq LLM instance."""
        from langchain_groq import ChatGroq
        
        return ChatGroq(
            api_key=self.api_key,
            model=self.model
        )
    
    def list_models(self) -> List[str]:
        """List available Groq models."""
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Groq pricing (very affordable)."""
        # Groq: $0.00027/1K input, $0.00027/1K output
        cost_per_1k = 0.00027
        
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * cost_per_1k
