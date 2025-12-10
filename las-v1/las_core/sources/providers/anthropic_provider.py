"""
Anthropic Provider - Claude API implementation.
"""

from typing import List, Dict, Iterator, Union
from anthropic import Anthropic
from sources.providers.base_provider import BaseProvider, ProviderConfig

class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.api_key:
            import os
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using Claude API."""
        client = Anthropic(api_key=self.api_key)
        
        try:
            # Extract system message if present
            system_msg = None
            filtered_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    system_msg = msg.get("content")
                else:
                    filtered_messages.append(msg)
            
            response = client.messages.create(
                model=self.model,
                messages=filtered_messages,
                system=system_msg,
                max_tokens=kwargs.get("max_tokens", 1024),
                stream=stream
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}")
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response."""
        for event in response:
            if event.type == "content_block_delta":
                if hasattr(event.delta, 'text'):
                    yield event.delta.text
    
    def get_langchain_llm(self):
        """Get LangChain Claude LLM instance."""
        from langchain_anthropic import ChatAnthropic
        
        return ChatAnthropic(
            api_key=self.api_key,
            model=self.model
        )
    
    def list_models(self) -> List[str]:
        """List available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Claude pricing."""
        # Claude 3.5 Sonnet: $3/1M input, $15/1M output
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        
        return input_cost + output_cost
