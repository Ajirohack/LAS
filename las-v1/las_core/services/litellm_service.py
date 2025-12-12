"""
LiteLLM Unified Service - Single interface for 100+ LLM providers.

This module provides a lightweight, powerful integration with LiteLLM SDK,
supporting OpenAI-compatible APIs, Gemini, Ollama, HuggingFace, Groq,
OpenRouter, and many more providers with unified function calling,
streaming, vision, and tool use capabilities.

Documentation: https://docs.litellm.ai
"""

import os
import asyncio
from typing import (
    List, Dict, Any, Optional, Union, Iterator, AsyncIterator,
    Literal, Callable
)
from dataclasses import dataclass, field
from enum import Enum

# LiteLLM SDK imports
try:
    import litellm
    from litellm import (
        completion,
        acompletion,
        embedding,
        aembedding,
        image_generation,
        transcription,
        speech,
        ModelResponse,
        EmbeddingResponse,
    )
    from litellm.utils import CustomStreamWrapper
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("[LiteLLM] LiteLLM not installed. Run: pip install litellm")

from sources.logger import Logger

logger = Logger("litellm_service.log")


class LiteLLMProvider(str, Enum):
    """Supported LiteLLM providers."""
    # OpenAI-compatible
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    TOGETHER = "together_ai"
    DEEPSEEK = "deepseek"
    FIREWORKS = "fireworks_ai"
    PERPLEXITY = "perplexity"
    ANYSCALE = "anyscale"
    
    # Google
    GEMINI = "gemini"
    VERTEX_AI = "vertex_ai"
    
    # Anthropic
    ANTHROPIC = "anthropic"
    
    # Local/Self-hosted
    OLLAMA = "ollama"
    OLLAMA_CHAT = "ollama_chat"
    VLLM = "vllm"
    HUGGINGFACE = "huggingface"
    
    # Cloud
    AZURE = "azure"
    BEDROCK = "bedrock"
    SAGEMAKER = "sagemaker"
    
    # Specialized
    COHERE = "cohere"
    MISTRAL = "mistral"
    REPLICATE = "replicate"
    
    # Custom OpenAI-compatible
    CUSTOM_OPENAI = "custom_openai"


@dataclass
class LiteLLMConfig:
    """Configuration for LiteLLM service."""
    # Default provider and model
    default_provider: str = "ollama"
    default_model: str = "llama3.2"
    
    # API Keys (loaded from environment)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    together_api_key: Optional[str] = None
    
    # Ollama settings
    ollama_base_url: str = "http://localhost:11434"
    
    # Custom OpenAI-compatible endpoints
    custom_api_base: Optional[str] = None
    custom_api_key: Optional[str] = None
    
    # Generation defaults
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    
    # Features
    enable_caching: bool = True
    enable_cost_tracking: bool = True
    enable_logging: bool = True
    
    # Callbacks
    success_callback: List[str] = field(default_factory=list)
    failure_callback: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Load API keys from environment."""
        self.openai_api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = self.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = self.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = self.groq_api_key or os.getenv("GROQ_API_KEY")
        self.openrouter_api_key = self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.huggingface_api_key = self.huggingface_api_key or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        self.together_api_key = self.together_api_key or os.getenv("TOGETHER_API_KEY") or os.getenv("TOGETHERAI_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", self.ollama_base_url)


@dataclass
class ToolDefinition:
    """Tool/Function definition for function calling."""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    def to_openai_format(self) -> Dict[str, Any]:
        """Convert to OpenAI function format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class LiteLLMService:
    """
    Unified LLM service powered by LiteLLM SDK.
    
    Supports:
    - 100+ LLM providers with unified API
    - Streaming responses
    - Function calling / Tool use
    - Vision (image understanding)
    - Embeddings
    - Audio transcription & TTS
    - Cost tracking
    - Caching
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LiteLLMService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM is not installed. Run: pip install litellm")
        
        self.config = LiteLLMConfig()
        self._setup_litellm()
        self._initialized = True
        logger.info("LiteLLM Service initialized")
    
    def _setup_litellm(self):
        """Configure LiteLLM global settings."""
        # Set API keys
        if self.config.openai_api_key:
            litellm.openai_key = self.config.openai_api_key
        if self.config.anthropic_api_key:
            litellm.anthropic_key = self.config.anthropic_api_key
        if self.config.groq_api_key:
            litellm.groq_key = self.config.groq_api_key
        if self.config.huggingface_api_key:
            litellm.huggingface_key = self.config.huggingface_api_key
        if self.config.openrouter_api_key:
            litellm.openrouter_key = self.config.openrouter_api_key
        if self.config.together_api_key:
            litellm.togetherai_api_key = self.config.together_api_key
        
        # Enable features
        litellm.drop_params = True  # Drop unsupported params instead of erroring
        
        # Setup callbacks
        if self.config.enable_logging:
            litellm.success_callback = self.config.success_callback or []
            litellm.failure_callback = self.config.failure_callback or []
        
        logger.info("LiteLLM configured with available providers")
    
    def update_config(self, **kwargs):
        """Update configuration dynamically."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._setup_litellm()
    
    # ========== MODEL NAMING HELPERS ==========
    
    def _format_model_name(
        self,
        model: str,
        provider: Optional[str] = None
    ) -> str:
        """
        Format model name for LiteLLM.
        
        LiteLLM uses format: provider/model_name
        Examples:
            - openai/gpt-4o
            - anthropic/claude-3-5-sonnet-20241022
            - ollama/llama3.2
            - gemini/gemini-1.5-pro
            - groq/llama-3.3-70b-versatile
            - openrouter/meta-llama/llama-3.3-70b-instruct
        """
        # If already has provider prefix, return as-is
        if "/" in model and provider is None:
            return model
        
        provider = provider or self.config.default_provider
        
        # Handle special cases
        if provider == "ollama":
            return f"ollama/{model}"
        elif provider == "ollama_chat":
            return f"ollama_chat/{model}"
        elif provider == "openai":
            return f"openai/{model}"
        elif provider == "anthropic":
            return f"anthropic/{model}"
        elif provider == "gemini":
            return f"gemini/{model}"
        elif provider == "groq":
            return f"groq/{model}"
        elif provider == "openrouter":
            return f"openrouter/{model}"
        elif provider == "together_ai":
            return f"together_ai/{model}"
        elif provider == "huggingface":
            return f"huggingface/{model}"
        elif provider == "deepseek":
            return f"deepseek/{model}"
        elif provider == "custom_openai":
            # Custom endpoints use the model name directly with api_base
            return model
        else:
            return f"{provider}/{model}"
    
    # ========== CHAT COMPLETION ==========
    
    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Union[ToolDefinition, Dict]]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        response_format: Optional[Dict] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> Union[ModelResponse, Iterator[Any]]:
        """
        Generate chat completion using LiteLLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (e.g., 'gpt-4o', 'llama3.2')
            provider: Provider name (e.g., 'openai', 'ollama')
            stream: Enable streaming response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: List of tool/function definitions
            tool_choice: Tool selection mode
            response_format: Response format (e.g., {"type": "json_object"})
            api_base: Custom API base URL
            api_key: Custom API key
            **kwargs: Additional LiteLLM parameters
            
        Returns:
            ModelResponse or stream iterator
        """
        model = model or self.config.default_model
        formatted_model = self._format_model_name(model, provider)
        
        # Build completion kwargs
        completion_kwargs = {
            "model": formatted_model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        # Add tools if provided
        if tools:
            formatted_tools = []
            for tool in tools:
                if isinstance(tool, ToolDefinition):
                    formatted_tools.append(tool.to_openai_format())
                else:
                    formatted_tools.append(tool)
            completion_kwargs["tools"] = formatted_tools
            if tool_choice:
                completion_kwargs["tool_choice"] = tool_choice
        
        # Add response format
        if response_format:
            completion_kwargs["response_format"] = response_format
        
        # Custom API base for OpenAI-compatible endpoints
        if api_base or self.config.custom_api_base:
            completion_kwargs["api_base"] = api_base or self.config.custom_api_base
        
        if api_key or self.config.custom_api_key:
            completion_kwargs["api_key"] = api_key or self.config.custom_api_key
        
        # Ollama-specific base URL
        if provider == "ollama" or (not provider and self.config.default_provider == "ollama"):
            if not api_base:
                completion_kwargs["api_base"] = self.config.ollama_base_url
        
        # Merge additional kwargs
        completion_kwargs.update(kwargs)
        
        logger.info(f"Chat completion: model={formatted_model}, stream={stream}")
        
        try:
            response = completion(**completion_kwargs)
            return response
        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise
    
    async def achat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Union[ToolDefinition, Dict]]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        response_format: Optional[Dict] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ) -> Union[ModelResponse, AsyncIterator[Any]]:
        """Async version of chat_completion."""
        model = model or self.config.default_model
        formatted_model = self._format_model_name(model, provider)
        
        completion_kwargs = {
            "model": formatted_model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }
        
        if tools:
            formatted_tools = []
            for tool in tools:
                if isinstance(tool, ToolDefinition):
                    formatted_tools.append(tool.to_openai_format())
                else:
                    formatted_tools.append(tool)
            completion_kwargs["tools"] = formatted_tools
            if tool_choice:
                completion_kwargs["tool_choice"] = tool_choice
        
        if response_format:
            completion_kwargs["response_format"] = response_format
        
        if api_base or self.config.custom_api_base:
            completion_kwargs["api_base"] = api_base or self.config.custom_api_base
        
        if api_key or self.config.custom_api_key:
            completion_kwargs["api_key"] = api_key or self.config.custom_api_key
        
        if provider == "ollama" or (not provider and self.config.default_provider == "ollama"):
            if not api_base:
                completion_kwargs["api_base"] = self.config.ollama_base_url
        
        completion_kwargs.update(kwargs)
        
        logger.info(f"Async chat completion: model={formatted_model}")
        
        try:
            response = await acompletion(**completion_kwargs)
            return response
        except Exception as e:
            logger.error(f"Async chat completion error: {e}")
            raise
    
    # ========== EMBEDDINGS ==========
    
    def create_embedding(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-3-small",
        provider: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """
        Create embeddings using LiteLLM.
        
        Args:
            input: Text or list of texts to embed
            model: Embedding model name
            provider: Provider name
            
        Returns:
            EmbeddingResponse with embedding vectors
        """
        formatted_model = self._format_model_name(model, provider or "openai")
        
        try:
            response = embedding(
                model=formatted_model,
                input=input,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
    
    async def acreate_embedding(
        self,
        input: Union[str, List[str]],
        model: str = "text-embedding-3-small",
        provider: Optional[str] = None,
        **kwargs
    ) -> EmbeddingResponse:
        """Async version of create_embedding."""
        formatted_model = self._format_model_name(model, provider or "openai")
        
        try:
            response = await aembedding(
                model=formatted_model,
                input=input,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Async embedding error: {e}")
            raise
    
    # ========== VISION (Image Understanding) ==========
    
    def vision_completion(
        self,
        prompt: str,
        image_url: str,
        model: str = "gpt-4o",
        provider: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Vision completion for image understanding.
        
        Args:
            prompt: Text prompt about the image
            image_url: URL or base64 of the image
            model: Vision-capable model
            provider: Provider name
            
        Returns:
            ModelResponse with image analysis
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    }
                ]
            }
        ]
        
        return self.chat_completion(
            messages=messages,
            model=model,
            provider=provider,
            **kwargs
        )
    
    # ========== IMAGE GENERATION ==========
    
    def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        n: int = 1,
        size: str = "1024x1024",
        **kwargs
    ) -> Any:
        """
        Generate images using LiteLLM.
        
        Args:
            prompt: Image description
            model: Image generation model
            n: Number of images
            size: Image size
            
        Returns:
            Image generation response
        """
        try:
            response = image_generation(
                prompt=prompt,
                model=model,
                n=n,
                size=size,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            raise
    
    # ========== AUDIO (STT & TTS) ==========
    
    def transcribe_audio(
        self,
        file: Any,
        model: str = "whisper-1",
        **kwargs
    ) -> Any:
        """
        Transcribe audio to text.
        
        Args:
            file: Audio file object
            model: Transcription model
            
        Returns:
            Transcription response
        """
        try:
            response = transcription(
                model=model,
                file=file,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise
    
    def text_to_speech(
        self,
        input: str,
        model: str = "tts-1",
        voice: str = "alloy",
        **kwargs
    ) -> Any:
        """
        Convert text to speech.
        
        Args:
            input: Text to convert
            model: TTS model
            voice: Voice selection
            
        Returns:
            Audio response
        """
        try:
            response = speech(
                model=model,
                input=input,
                voice=voice,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    # ========== FUNCTION CALLING / TOOL USE ==========
    
    def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[ToolDefinition],
        tool_handlers: Dict[str, Callable],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat with automatic tool execution.
        
        Args:
            messages: Conversation messages
            tools: List of tool definitions
            tool_handlers: Dict mapping tool names to handler functions
            model: Model name
            provider: Provider name
            max_iterations: Max tool execution loops
            
        Returns:
            Final response with tool results
        """
        iteration = 0
        all_tool_calls = []
        
        while iteration < max_iterations:
            response = self.chat_completion(
                messages=messages,
                model=model,
                provider=provider,
                tools=tools,
                **kwargs
            )
            
            message = response.choices[0].message
            
            # Check for tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    
                    if tool_name in tool_handlers:
                        import json
                        args = json.loads(tool_call.function.arguments)
                        
                        try:
                            result = tool_handlers[tool_name](**args)
                            tool_result = str(result)
                        except Exception as e:
                            tool_result = f"Error: {e}"
                        
                        all_tool_calls.append({
                            "name": tool_name,
                            "arguments": args,
                            "result": tool_result
                        })
                        
                        # Add tool result
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Unknown tool: {tool_name}"
                        })
                
                iteration += 1
            else:
                # No more tool calls, return final response
                return {
                    "response": message.content,
                    "tool_calls": all_tool_calls,
                    "iterations": iteration,
                    "model": response.model,
                    "usage": response.usage._asdict() if response.usage else None
                }
        
        # Max iterations reached
        return {
            "response": message.content if message else None,
            "tool_calls": all_tool_calls,
            "iterations": iteration,
            "max_iterations_reached": True
        }
    
    # ========== MODEL LISTING ==========
    
    def list_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available models for a provider.
        
        Args:
            provider: Provider name (optional)
            
        Returns:
            List of model info dicts
        """
        models = []
        
        # Popular models by provider
        model_catalog = {
            "openai": [
                {"id": "gpt-4o", "context": 128000, "features": ["vision", "tools", "json"]},
                {"id": "gpt-4o-mini", "context": 128000, "features": ["vision", "tools", "json"]},
                {"id": "gpt-4-turbo", "context": 128000, "features": ["vision", "tools", "json"]},
                {"id": "gpt-3.5-turbo", "context": 16385, "features": ["tools", "json"]},
                {"id": "o1", "context": 200000, "features": ["reasoning"]},
                {"id": "o1-mini", "context": 128000, "features": ["reasoning"]},
            ],
            "anthropic": [
                {"id": "claude-3-5-sonnet-20241022", "context": 200000, "features": ["vision", "tools"]},
                {"id": "claude-3-5-haiku-20241022", "context": 200000, "features": ["vision", "tools"]},
                {"id": "claude-3-opus-20240229", "context": 200000, "features": ["vision", "tools"]},
            ],
            "gemini": [
                {"id": "gemini-2.0-flash-exp", "context": 1000000, "features": ["vision", "tools", "multimodal"]},
                {"id": "gemini-1.5-pro", "context": 2000000, "features": ["vision", "tools"]},
                {"id": "gemini-1.5-flash", "context": 1000000, "features": ["vision", "tools"]},
            ],
            "groq": [
                {"id": "llama-3.3-70b-versatile", "context": 128000, "features": ["tools"]},
                {"id": "llama-3.1-8b-instant", "context": 128000, "features": ["tools"]},
                {"id": "mixtral-8x7b-32768", "context": 32768, "features": []},
            ],
            "ollama": [
                {"id": "llama3.2", "context": 128000, "features": ["local"]},
                {"id": "llama3.2:1b", "context": 128000, "features": ["local"]},
                {"id": "qwen2.5:7b", "context": 128000, "features": ["local"]},
                {"id": "mistral", "context": 32000, "features": ["local"]},
                {"id": "codellama", "context": 16000, "features": ["local", "code"]},
            ],
            "openrouter": [
                {"id": "anthropic/claude-3.5-sonnet", "context": 200000, "features": ["vision", "tools"]},
                {"id": "openai/gpt-4o", "context": 128000, "features": ["vision", "tools"]},
                {"id": "meta-llama/llama-3.3-70b-instruct", "context": 128000, "features": ["tools"]},
                {"id": "google/gemini-pro-1.5", "context": 2000000, "features": ["vision"]},
            ],
            "huggingface": [
                {"id": "meta-llama/Llama-3.2-3B-Instruct", "context": 128000, "features": []},
                {"id": "mistralai/Mistral-7B-Instruct-v0.3", "context": 32000, "features": []},
                {"id": "Qwen/Qwen2.5-7B-Instruct", "context": 128000, "features": []},
            ],
            "together_ai": [
                {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "context": 128000, "features": ["tools"]},
                {"id": "mistralai/Mixtral-8x22B-Instruct-v0.1", "context": 65536, "features": []},
            ],
            "deepseek": [
                {"id": "deepseek-chat", "context": 64000, "features": ["code", "tools"]},
                {"id": "deepseek-reasoner", "context": 64000, "features": ["reasoning"]},
            ],
        }
        
        if provider:
            provider = provider.lower()
            if provider in model_catalog:
                for m in model_catalog[provider]:
                    models.append({
                        "id": m["id"],
                        "provider": provider,
                        "context_length": m.get("context", 4096),
                        "features": m.get("features", []),
                        "litellm_model": f"{provider}/{m['id']}"
                    })
        else:
            # Return all models
            for prov, prov_models in model_catalog.items():
                for m in prov_models:
                    models.append({
                        "id": m["id"],
                        "provider": prov,
                        "context_length": m.get("context", 4096),
                        "features": m.get("features", []),
                        "litellm_model": f"{prov}/{m['id']}"
                    })
        
        return models
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """List all available providers with configuration status."""
        providers = []
        
        provider_info = {
            "openai": {
                "name": "OpenAI",
                "key_env": "OPENAI_API_KEY",
                "configured": bool(self.config.openai_api_key),
                "features": ["chat", "vision", "tools", "embeddings", "image_gen", "tts", "stt"],
            },
            "anthropic": {
                "name": "Anthropic (Claude)",
                "key_env": "ANTHROPIC_API_KEY",
                "configured": bool(self.config.anthropic_api_key),
                "features": ["chat", "vision", "tools"],
            },
            "gemini": {
                "name": "Google Gemini",
                "key_env": "GEMINI_API_KEY",
                "configured": bool(self.config.gemini_api_key),
                "features": ["chat", "vision", "tools", "embeddings"],
            },
            "groq": {
                "name": "Groq",
                "key_env": "GROQ_API_KEY",
                "configured": bool(self.config.groq_api_key),
                "features": ["chat", "fast_inference"],
            },
            "ollama": {
                "name": "Ollama (Local)",
                "key_env": None,
                "configured": True,  # No key required
                "features": ["chat", "local", "embeddings"],
                "base_url": self.config.ollama_base_url,
            },
            "openrouter": {
                "name": "OpenRouter",
                "key_env": "OPENROUTER_API_KEY",
                "configured": bool(self.config.openrouter_api_key),
                "features": ["chat", "multi_provider", "vision", "tools"],
            },
            "huggingface": {
                "name": "HuggingFace",
                "key_env": "HF_TOKEN",
                "configured": bool(self.config.huggingface_api_key),
                "features": ["chat", "embeddings"],
            },
            "together_ai": {
                "name": "Together AI",
                "key_env": "TOGETHER_API_KEY",
                "configured": bool(self.config.together_api_key),
                "features": ["chat", "fast_inference", "tools"],
            },
        }
        
        for key, info in provider_info.items():
            providers.append({
                "id": key,
                **info
            })
        
        return providers
    
    # ========== COST TRACKING ==========
    
    def get_cost_estimate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, Any]:
        """
        Estimate cost for token usage.
        
        Uses LiteLLM's built-in cost tracking.
        """
        try:
            from litellm import cost_per_token
            
            cost = cost_per_token(
                model=model,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens
            )
            
            return {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": cost.get("prompt_tokens_cost", 0),
                "output_cost": cost.get("completion_tokens_cost", 0),
                "total_cost": cost.get("prompt_tokens_cost", 0) + cost.get("completion_tokens_cost", 0)
            }
        except Exception:
            return {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_cost": 0,
                "note": "Cost calculation not available for this model"
            }


# Singleton accessor
def get_litellm_service() -> LiteLLMService:
    """Get the LiteLLM service singleton."""
    return LiteLLMService()
