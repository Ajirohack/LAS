"""
LiteLLM Provider - Integrates LiteLLM SDK with the existing provider architecture.

This provider uses LiteLLM as the backend, providing access to 100+ LLM providers
through the unified LAS provider interface.
"""

import os
from typing import List, Dict, Any, Optional, Iterator, Union

from sources.providers.base_provider import BaseProvider, ProviderConfig
from sources.logger import Logger

logger = Logger("litellm_provider.log")


class LiteLLMProvider(BaseProvider):
    """
    LiteLLM-powered provider for unified LLM access.
    
    Supports all LiteLLM providers including:
    - OpenAI, Azure OpenAI
    - Anthropic (Claude)
    - Google (Gemini, Vertex AI)
    - Ollama (local)
    - Groq, Together AI, OpenRouter
    - HuggingFace
    - And 100+ more...
    
    Usage:
        provider = LiteLLMProvider(ProviderConfig(
            model="ollama/llama3.2",  # or "openai/gpt-4o", "gemini/gemini-1.5-pro", etc.
        ))
        response = provider.chat_completion([{"role": "user", "content": "Hello!"}])
    """
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        
        # Import LiteLLM
        try:
            import litellm
            from litellm import completion, acompletion
            self._litellm = litellm
            self._completion = completion
            self._acompletion = acompletion
            self._available = True
        except ImportError:
            logger.error("LiteLLM not installed. Run: pip install litellm")
            self._available = False
            raise ImportError("LiteLLM is required. Install with: pip install litellm")
        
        # Parse model string (format: provider/model or just model)
        self._parse_model_string()
        
        # Setup API keys
        self._setup_api_keys()
        
        logger.info(f"LiteLLM Provider initialized: {self.model} (provider: {self._llm_provider})")
    
    @property
    def provider_name(self) -> str:
        return "litellm"
    
    def _parse_model_string(self):
        """Parse model string to extract provider prefix."""
        model = self.model
        
        if "/" in model:
            # Model already has provider prefix
            parts = model.split("/", 1)
            self._llm_provider = parts[0]
            self._model_name = parts[1]
            self._full_model = model
        else:
            # No provider prefix - use default or detect
            self._llm_provider = self.config.extra.get("provider", "ollama") if self.config.extra else "ollama"
            self._model_name = model
            self._full_model = f"{self._llm_provider}/{model}"
    
    def _setup_api_keys(self):
        """Setup API keys for LiteLLM."""
        # Read from config extra or environment
        extra = self.config.extra or {}
        
        # Map provider to environment variable
        api_key_map = {
            "openai": ("OPENAI_API_KEY", "openai_key"),
            "anthropic": ("ANTHROPIC_API_KEY", "anthropic_key"),
            "gemini": ("GEMINI_API_KEY", None),
            "google": ("GOOGLE_API_KEY", None),
            "groq": ("GROQ_API_KEY", "groq_key"),
            "openrouter": ("OPENROUTER_API_KEY", "openrouter_key"),
            "huggingface": ("HF_TOKEN", "huggingface_key"),
            "together_ai": ("TOGETHER_API_KEY", "togetherai_api_key"),
            "together": ("TOGETHER_API_KEY", "togetherai_api_key"),
            "deepseek": ("DEEPSEEK_API_KEY", None),
            "mistral": ("MISTRAL_API_KEY", None),
            "cohere": ("COHERE_API_KEY", "cohere_key"),
        }
        
        # Set API key if provider requires one
        provider = self._llm_provider.lower()
        if provider in api_key_map:
            env_var, litellm_attr = api_key_map[provider]
            api_key = self.api_key or extra.get("api_key") or os.getenv(env_var)
            
            if api_key and litellm_attr:
                setattr(self._litellm, litellm_attr, api_key)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        Generate chat completion using LiteLLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional LiteLLM parameters
            
        Returns:
            Complete response string or iterator of chunks
        """
        if not self._available:
            raise RuntimeError("LiteLLM is not available")
        
        # Build completion kwargs
        completion_kwargs = {
            "model": self._full_model,
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        # Add API base if provided
        if self.base_url:
            completion_kwargs["api_base"] = self.base_url
        elif self._llm_provider == "ollama":
            completion_kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Add API key if provided
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key
        
        # Add tools if provided
        if "tools" in kwargs:
            completion_kwargs["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            completion_kwargs["tool_choice"] = kwargs["tool_choice"]
        
        # Add response format if provided
        if "response_format" in kwargs:
            completion_kwargs["response_format"] = kwargs["response_format"]
        
        # Pass through other kwargs
        for key in ["top_p", "presence_penalty", "frequency_penalty", "stop", "n"]:
            if key in kwargs:
                completion_kwargs[key] = kwargs[key]
        
        try:
            response = self._completion(**completion_kwargs)
            
            if stream:
                return self._stream_generator(response)
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise
    
    def _stream_generator(self, response) -> Iterator[str]:
        """Generate streaming response chunks."""
        try:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise
    
    async def achat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[str, Any]:
        """Async chat completion."""
        if not self._available:
            raise RuntimeError("LiteLLM is not available")
        
        completion_kwargs = {
            "model": self._full_model,
            "messages": messages,
            "stream": stream,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }
        
        if self.base_url:
            completion_kwargs["api_base"] = self.base_url
        elif self._llm_provider == "ollama":
            completion_kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        if self.api_key:
            completion_kwargs["api_key"] = self.api_key
        
        for key in ["tools", "tool_choice", "response_format", "top_p", "stop"]:
            if key in kwargs:
                completion_kwargs[key] = kwargs[key]
        
        try:
            response = await self._acompletion(**completion_kwargs)
            
            if stream:
                return response  # Return async iterator
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Async chat completion error: {e}")
            raise
    
    def get_langchain_llm(self):
        """
        Get LangChain LLM instance.
        
        Uses ChatLiteLLM from langchain-community.
        """
        try:
            from langchain_community.chat_models import ChatLiteLLM
            
            llm_kwargs = {
                "model": self._full_model,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            }
            
            if self.base_url:
                llm_kwargs["api_base"] = self.base_url
            elif self._llm_provider == "ollama":
                llm_kwargs["api_base"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            if self.api_key:
                llm_kwargs["api_key"] = self.api_key
            
            return ChatLiteLLM(**llm_kwargs)
            
        except ImportError:
            logger.warning("langchain-community not installed, falling back to generic LLM")
            
            # Fallback: try to use provider-specific LangChain integration
            try:
                if self._llm_provider == "openai":
                    from langchain_openai import ChatOpenAI
                    return ChatOpenAI(
                        model=self._model_name,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                    )
                elif self._llm_provider == "anthropic":
                    from langchain_anthropic import ChatAnthropic
                    return ChatAnthropic(
                        model=self._model_name,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                    )
                elif self._llm_provider in ["gemini", "google"]:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    return ChatGoogleGenerativeAI(
                        model=self._model_name,
                        temperature=self.config.temperature,
                        max_output_tokens=self.config.max_tokens,
                    )
                elif self._llm_provider == "groq":
                    from langchain_groq import ChatGroq
                    return ChatGroq(
                        model=self._model_name,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens,
                    )
                elif self._llm_provider == "ollama":
                    from langchain_community.chat_models import ChatOllama
                    return ChatOllama(
                        model=self._model_name,
                        temperature=self.config.temperature,
                        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                    )
            except ImportError as e:
                logger.error(f"Could not create LangChain LLM: {e}")
                return None
    
    def list_models(self) -> List[str]:
        """
        List available models.
        
        Returns models from the LiteLLM service's model catalog.
        """
        try:
            from services.litellm_service import get_litellm_service
            svc = get_litellm_service()
            models = svc.list_models(provider=self._llm_provider)
            return [m["id"] for m in models]
        except Exception:
            # Fallback: return common models for the provider
            model_lists = {
                "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
                "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                "groq": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                "ollama": ["llama3.2", "llama3.2:1b", "qwen2.5:7b", "mistral", "codellama"],
                "openrouter": ["anthropic/claude-3.5-sonnet", "openai/gpt-4o", "meta-llama/llama-3.3-70b-instruct"],
            }
            return model_lists.get(self._llm_provider, [self._model_name])
    
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        if not self.model:
            raise ValueError("LiteLLM: model is required")
        
        if not self._available:
            raise ValueError("LiteLLM: litellm package not available")
        
        # Check if API key is required and present
        providers_requiring_key = ["openai", "anthropic", "gemini", "groq", "openrouter", "together_ai"]
        
        if self._llm_provider in providers_requiring_key:
            if not self.api_key:
                env_vars = {
                    "openai": "OPENAI_API_KEY",
                    "anthropic": "ANTHROPIC_API_KEY",
                    "gemini": "GEMINI_API_KEY",
                    "groq": "GROQ_API_KEY",
                    "openrouter": "OPENROUTER_API_KEY",
                    "together_ai": "TOGETHER_API_KEY",
                }
                env_var = env_vars.get(self._llm_provider, f"{self._llm_provider.upper()}_API_KEY")
                if not os.getenv(env_var):
                    logger.warning(f"LiteLLM: No API key found for {self._llm_provider}. Set {env_var}")
        
        return True
    
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        # All LiteLLM providers support streaming
        return True
    
    def supports_function_calling(self) -> bool:
        """Check if provider supports function calling."""
        function_calling_providers = [
            "openai", "anthropic", "gemini", "groq", "openrouter", 
            "together_ai", "mistral", "deepseek"
        ]
        return self._llm_provider in function_calling_providers
    
    def supports_vision(self) -> bool:
        """Check if the current model supports vision/images."""
        vision_models = [
            "gpt-4o", "gpt-4-turbo", "gpt-4-vision",
            "claude-3", "claude-3-5",
            "gemini-1.5", "gemini-2",
            "llava", "bakllava"
        ]
        return any(vm in self._model_name.lower() for vm in vision_models)
    
    def get_cost_per_token(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage."""
        try:
            from litellm import cost_per_token
            
            cost = cost_per_token(
                model=self._full_model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens
            )
            
            return cost.get("prompt_tokens_cost", 0) + cost.get("completion_tokens_cost", 0)
        except Exception:
            return 0.0
    
    def __repr__(self) -> str:
        return f"LiteLLMProvider(model={self._full_model}, provider={self._llm_provider})"
