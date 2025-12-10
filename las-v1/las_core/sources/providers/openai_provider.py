"""
OpenAI Provider - OpenAI API implementation.
"""

from typing import List, Dict, Iterator, Union
from langchain_openai import ChatOpenAI
from openai import OpenAI
from sources.providers.base_provider import BaseProvider, ProviderConfig

class OpenAIProvider(BaseProvider):
    """OpenAI API provider with GPT models."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.api_key:
            import os
            self.api_key = os.getenv("OPENAI_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using OpenAI API."""
        client = OpenAI(api_key=self.api_key)
        
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
            raise RuntimeError(f"OpenAI API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response."""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    yield delta.content
    
    def get_langchain_llm(self):
        """Get LangChain ChatOpenAI instance."""
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model
        )
    
    def list_models(self) -> List[str]:
        """List available OpenAI models."""
        return [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-4-turbo-preview",
            "gpt-4o",
            "gpt-4o-mini"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def supports_function_calling(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on GPT-4 pricing."""
        # GPT-4 pricing (approximate)
        cost_per_1k_input = 0.03
        cost_per_1k_output = 0.06
        
        input_cost = (input_tokens / 1000) * cost_per_1k_input
        output_cost = (output_tokens / 1000) * cost_per_1k_output
        
        return input_cost + output_cost
