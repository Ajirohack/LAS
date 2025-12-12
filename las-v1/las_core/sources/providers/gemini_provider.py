"""
Google Gemini Provider - Access Google's Gemini models.

Supports:
- Gemini 1.5 Flash (free)
- Gemini 1.5 Pro
- Gemini 2.0 Flash (experimental, free)
- Streaming and non-streaming responses
- Full LangChain integration
"""

import os
from typing import List, Dict, Any, Optional, Iterator
from sources.providers.base_provider import BaseProvider, ProviderConfig
from sources.logger import Logger

logger = Logger("gemini_provider.log")


class GeminiProvider(BaseProvider):
    """
    Google Gemini provider.
    
    Free models: gemini-1.5-flash, gemini-2.0-flash-exp
    Pro models: gemini-1.5-pro, gemini-2.0-pro-exp
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set. Requests will fail.")
        
        # Normalize model name
        self.model = self._normalize_model_name(config.model)
        
        logger.info(f"Gemini Provider initialized: {self.model}")
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize Gemini model names."""
        # Map common aliases to official names
        aliases = {
            "gemini-flash": "gemini-1.5-flash",
            "gemini-pro": "gemini-1.5-pro",
            "gemini-1.5": "gemini-1.5-flash",
            "gemini-2": "gemini-2.0-flash-exp",
            "gemini-2-flash": "gemini-2.0-flash-exp",
        }
        
        model_lower = model.lower()
        return aliases.get(model_lower, model)
    
    def get_langchain_llm(self):
        """Get LangChain ChatGoogleGenerativeAI instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=self.config.temperature or 0.7,
                max_output_tokens=self.config.max_tokens,
                convert_system_message_to_human=True  # Gemini doesn't support system messages
            )
            
            logger.info(f"Created LangChain ChatGoogleGenerativeAI: {self.model}")
            return llm
            
        except ImportError:
            logger.error("langchain-google-genai not installed. Install with: pip install langchain-google-genai")
            raise
        except Exception as e:
            logger.error(f"Failed to create Gemini LLM: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Generate chat completion using Google Gemini API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Response dict or generator if streaming
        """
        try:
            import google.generativeai as genai
            
            # Configure API key
            genai.configure(api_key=self.api_key)
            
            # Create model
            model = genai.GenerativeModel(self.model)
            
            # Convert messages to Gemini format
            # Gemini doesn't support system messages, so we prepend them to first user message
            gemini_messages = []
            system_prompt = None
            
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                
                if role == "system":
                    system_prompt = content
                elif role == "user":
                    if system_prompt:
                        content = f"{system_prompt}\n\n{content}"
                        system_prompt = None
                    gemini_messages.append({"role": "user", "parts": [content]})
                elif role == "assistant":
                    gemini_messages.append({"role": "model", "parts": [content]})
            
            # Generate config
            generation_config = {}
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs["temperature"]
            elif self.config.temperature is not None:
                generation_config["temperature"] = self.config.temperature
            
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs["max_tokens"]
            elif self.config.max_tokens:
                generation_config["max_output_tokens"] = self.config.max_tokens
            
            # Generate response
            if stream:
                response = model.generate_content(
                    gemini_messages,
                    generation_config=generation_config if generation_config else None,
                    stream=True
                )
                return self._stream_response(response)
            else:
                response = model.generate_content(
                    gemini_messages,
                    generation_config=generation_config if generation_config else None
                )
                return {
                    "content": response.text,
                    "model": self.model,
                    "done": True
                }
                
        except Exception as e:
            logger.error(f"Gemini chat completion failed: {e}")
            raise
    
    def _stream_response(self, response) -> Iterator[Dict[str, Any]]:
        """Stream response chunks."""
        for chunk in response:
            if hasattr(chunk, "text") and chunk.text:
                yield {
                    "content": chunk.text,
                    "done": False,
                    "model": self.model
                }
        
        # Final chunk
        yield {
            "content": "",
            "done": True,
            "model": self.model
        }
    
    def list_models(self) -> List[str]:
        """List available Gemini models."""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            
            models = []
            for model in genai.list_models():
                if "generateContent" in model.supported_generation_methods:
                    models.append(model.name.replace("models/", ""))
            
            logger.info(f"Listed {len(models)} Gemini models")
            return models
            
        except Exception as e:
            logger.error(f"Failed to list Gemini models: {e}")
            # Return known free models as fallback
            return self.get_free_models()
    
    def supports_streaming(self) -> bool:
        """Gemini supports streaming."""
        return True
    
    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "gemini"
    
    @staticmethod
    def get_free_models() -> List[str]:
        """Get list of free Gemini models."""
        return [
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-2.0-flash-exp",
            "gemini-exp-1206"  # Experimental model
        ]
