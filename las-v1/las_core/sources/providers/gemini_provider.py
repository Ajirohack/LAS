"""
Gemini Provider - Google Gemini API implementation.
"""

from typing import List, Dict, Iterator, Union
import google.generativeai as genai
from sources.providers.base_provider import BaseProvider, ProviderConfig

class GeminiProvider(BaseProvider):
    """Google Gemini API provider."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        if not self.api_key:
            import os
            self.api_key = os.getenv("GEMINI_API_KEY")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """Generate chat completion using Gemini API."""
        try:
            model = genai.GenerativeModel(self.model)
            
            # Convert messages to Gemini format
            prompt = self._convert_messages(messages)
            
            if stream:
                response = model.generate_content(prompt, stream=True)
                return self._handle_stream(response)
            else:
                response = model.generate_content(prompt)
                return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert chat messages to Gemini prompt format."""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)
    
    def _handle_stream(self, response) -> Iterator[str]:
        """Handle streaming response."""
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def get_langchain_llm(self):
        """Get LangChain Gemini LLM instance."""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key
        )
    
    def list_models(self) -> List[str]:
        """List available Gemini models."""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
    
    def supports_streaming(self) -> bool:
        return True
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Gemini Pro pricing."""
        # Gemini Pro: $0.00025 / 1K characters (approx 1K tokens = 4K chars)
        cost_per_1k_tokens = 0.001
        
        total_tokens = input_tokens + output_tokens
        return (total_tokens / 1000) * cost_per_1k_tokens
