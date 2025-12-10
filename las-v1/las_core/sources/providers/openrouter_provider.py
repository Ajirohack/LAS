"""
OpenRouter Provider - OpenRouter API implementation with cost tracking.
"""

from typing import List, Dict, Iterator, Union
from langchain_openai import ChatOpenAI
from openai import OpenAI
from sources.providers.base_provider import BaseProvider, ProviderConfig

class OpenRouterProvider(BaseProvider):
    """OpenRouter API provider with streaming and cost tracking."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.base_url:
            self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            import os
            self.api_key = os.getenv("OPENROUTER_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "openrouter"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using OpenRouter API."""
        from config.settings import settings
        from services.cost_tracker import get_cost_tracker, Provider as CostProvider
        
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": settings.app_url,
                "X-Title": settings.app_name
            }
        )
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                stream_options={"include_usage": True} if stream else {},
                **kwargs
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response with cost tracking."""
        from services.cost_tracker import get_cost_tracker, Provider as CostProvider
        
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
            
            # Track usage from final chunk
            if hasattr(chunk, 'usage') and chunk.usage:
                tracker = get_cost_tracker()
                tracker.track_usage(
                    provider=CostProvider.OPENROUTER,
                    input_tokens=chunk.usage.prompt_tokens,
                    output_tokens=chunk.usage.completion_tokens,
                    agent="user"
                )
    
    def get_langchain_llm(self):
        """Get LangChain ChatOpenAI instance for OpenRouter."""
        from config.settings import settings
        
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            default_headers={
                "HTTP-Referer": settings.app_url,
                "X-Title": settings.app_name
            }
        )
    
    def list_models(self) -> List[str]:
        """List available OpenRouter models."""
        # OpenRouter doesn't provide a models endpoint
        # Return commonly used models
        return [
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "google/gemini-pro",
            "meta-llama/llama-3.3-70b-instruct"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on OpenRouter pricing."""
        # Simplified - actual pricing varies by model
        cost_per_1m_input = 0.50
        cost_per_1m_output = 1.50
        
        input_cost = (input_tokens / 1_000_000) * cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * cost_per_1m_output
        
        return input_cost + output_cost
