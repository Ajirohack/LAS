"""
DeepSeek Provider - DeepSeek API implementation.
"""

from typing import List, Dict, Iterator, Union
from openai import OpenAI
from sources.providers.base_provider import BaseProvider, ProviderConfig

class DeepSeekProvider(BaseProvider):
    """DeepSeek API provider (OpenAI-compatible)."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.base_url:
            self.base_url = "https://api.deepseek.com"
        if not self.api_key:
            import os
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "deepseek"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using DeepSeek API."""
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
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
            raise RuntimeError(f"DeepSeek API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response."""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
    
    def get_langchain_llm(self):
        """Get LangChain LLM for DeepSeek."""
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model
        )
    
    def list_models(self) -> List[str]:
        """List available DeepSeek models."""
        return [
            "deepseek-chat",
            "deepseek-coder"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """DeepSeek pricing (very affordable)."""
        # DeepSeek: $0.14/1M input, $0.28/1M output
        input_cost = (input_tokens / 1_000_000) * 0.14
        output_cost = (output_tokens / 1_000_000) * 0.28
        
        return input_cost + output_cost
