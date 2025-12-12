"""
LiteLLM Router - API endpoints for LiteLLM service.

Provides REST API endpoints for:
- Chat completions (streaming & non-streaming)
- Model listing and provider management
- Embeddings
- Vision capabilities
- Audio (TTS/STT)
- Function calling / Tool use
- Cost estimation
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from sources.logger import Logger

router = APIRouter(prefix="/litellm", tags=["litellm", "llm"])
logger = Logger("litellm_router.log")


# ============== Request/Response Models ==============

class MessageRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    tool = "tool"


class Message(BaseModel):
    role: MessageRole
    content: Union[str, List[Dict[str, Any]]]  # Support text and multimodal content
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


class ToolFunction(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class Tool(BaseModel):
    type: str = "function"
    function: ToolFunction


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions."""
    model: str = Field(default="ollama/llama3.2", description="Model in format provider/model")
    messages: List[Message]
    stream: bool = Field(default=False, description="Enable streaming response")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=4096, ge=1)
    top_p: Optional[float] = Field(default=1.0, ge=0, le=1)
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict]] = None
    response_format: Optional[Dict[str, str]] = None
    
    # Provider override
    provider: Optional[str] = None
    api_base: Optional[str] = None  # For custom OpenAI-compatible endpoints
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "ollama/llama3.2",
                "messages": [
                    {"role": "user", "content": "Hello, what's 2+2?"}
                ],
                "stream": False,
                "temperature": 0.7
            }
        }


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions."""
    id: str
    model: str
    content: str
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    usage: Optional[Dict[str, int]] = None


class EmbeddingRequest(BaseModel):
    """Request for embeddings."""
    input: Union[str, List[str]]
    model: str = Field(default="text-embedding-3-small")
    provider: Optional[str] = Field(default="openai")


class VisionRequest(BaseModel):
    """Request for vision/image analysis."""
    prompt: str
    image_url: str
    model: str = Field(default="openai/gpt-4o")


class ModelInfo(BaseModel):
    """Model information."""
    id: str
    provider: str
    context_length: int
    features: List[str]
    litellm_model: str


class ProviderInfo(BaseModel):
    """Provider information."""
    id: str
    name: str
    configured: bool
    features: List[str]
    key_env: Optional[str] = None


class CostEstimateRequest(BaseModel):
    """Request for cost estimation."""
    model: str
    input_tokens: int
    output_tokens: int


# ============== Endpoints ==============

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    Create a chat completion using LiteLLM.
    
    Supports 100+ LLM providers with unified API:
    - OpenAI: openai/gpt-4o, openai/gpt-4o-mini
    - Anthropic: anthropic/claude-3-5-sonnet-20241022
    - Gemini: gemini/gemini-1.5-pro
    - Ollama: ollama/llama3.2, ollama/qwen2.5
    - Groq: groq/llama-3.3-70b-versatile
    - OpenRouter: openrouter/anthropic/claude-3.5-sonnet
    - And many more...
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        # Convert messages to dict format
        messages = [msg.model_dump(exclude_none=True) for msg in request.messages]
        
        # Build kwargs
        kwargs = {
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
        }
        
        if request.tools:
            kwargs["tools"] = [t.model_dump() for t in request.tools]
        if request.tool_choice:
            kwargs["tool_choice"] = request.tool_choice
        if request.response_format:
            kwargs["response_format"] = request.response_format
        if request.api_base:
            kwargs["api_base"] = request.api_base
        
        # Handle streaming
        if request.stream:
            response = await svc.achat_completion(
                messages=messages,
                model=request.model,
                provider=request.provider,
                stream=True,
                **kwargs
            )
            return StreamingResponse(
                _stream_response(response),
                media_type="text/event-stream"
            )
        
        # Non-streaming
        response = await svc.achat_completion(
            messages=messages,
            model=request.model,
            provider=request.provider,
            stream=False,
            **kwargs
        )
        
        # Extract response data
        message = response.choices[0].message
        
        return ChatCompletionResponse(
            id=response.id,
            model=response.model,
            content=message.content or "",
            finish_reason=response.choices[0].finish_reason,
            tool_calls=[tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
            usage=response.usage._asdict() if response.usage else None
        )
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"LiteLLM not available: {e}")
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _stream_response(response):
    """Generate SSE stream from LiteLLM response."""
    import json
    
    try:
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                data = {
                    "type": "token",
                    "content": chunk.choices[0].delta.content
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # Check for tool calls in streaming
            if chunk.choices and chunk.choices[0].delta.tool_calls:
                data = {
                    "type": "tool_call",
                    "tool_calls": [tc.model_dump() for tc in chunk.choices[0].delta.tool_calls]
                }
                yield f"data: {json.dumps(data)}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


@router.get("/models", response_model=List[ModelInfo])
async def list_models(provider: Optional[str] = None):
    """
    List available models.
    
    Optionally filter by provider (openai, anthropic, gemini, ollama, groq, etc.)
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        models = svc.list_models(provider=provider)
        return models
        
    except Exception as e:
        logger.error(f"List models error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """
    List all available LLM providers with their configuration status.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        providers = svc.list_providers()
        return providers
        
    except Exception as e:
        logger.error(f"List providers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings")
async def create_embeddings(request: EmbeddingRequest):
    """
    Create embeddings using LiteLLM.
    
    Supports OpenAI, Cohere, HuggingFace, Ollama, and more.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        response = await svc.acreate_embedding(
            input=request.input,
            model=request.model,
            provider=request.provider
        )
        
        return {
            "model": response.model,
            "data": [
                {
                    "index": item.index,
                    "embedding": item.embedding
                }
                for item in response.data
            ],
            "usage": response.usage._asdict() if response.usage else None
        }
        
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision")
async def vision_completion(request: VisionRequest):
    """
    Analyze an image using a vision-capable model.
    
    Supports GPT-4V, Claude 3, Gemini 1.5, LLaVA, etc.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        response = svc.vision_completion(
            prompt=request.prompt,
            image_url=request.image_url,
            model=request.model
        )
        
        return {
            "model": response.model,
            "content": response.choices[0].message.content,
            "usage": response.usage._asdict() if response.usage else None
        }
        
    except Exception as e:
        logger.error(f"Vision error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cost/estimate")
async def estimate_cost(request: CostEstimateRequest):
    """
    Estimate the cost for a given model and token count.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        estimate = svc.get_cost_estimate(
            model=request.model,
            input_tokens=request.input_tokens,
            output_tokens=request.output_tokens
        )
        
        return estimate
        
    except Exception as e:
        logger.error(f"Cost estimate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def litellm_health():
    """
    Check LiteLLM service health and configured providers.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        providers = svc.list_providers()
        configured_count = sum(1 for p in providers if p["configured"])
        
        return {
            "status": "healthy",
            "litellm_available": True,
            "providers_total": len(providers),
            "providers_configured": configured_count,
            "default_provider": svc.config.default_provider,
            "default_model": svc.config.default_model
        }
        
    except ImportError:
        return {
            "status": "unavailable",
            "litellm_available": False,
            "error": "LiteLLM not installed. Run: pip install litellm"
        }
    except Exception as e:
        return {
            "status": "error",
            "litellm_available": True,
            "error": str(e)
        }


@router.post("/config/update")
async def update_config(
    default_provider: Optional[str] = None,
    default_model: Optional[str] = None,
    ollama_base_url: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
):
    """
    Update LiteLLM service configuration.
    """
    try:
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        updates = {}
        if default_provider:
            updates["default_provider"] = default_provider
        if default_model:
            updates["default_model"] = default_model
        if ollama_base_url:
            updates["ollama_base_url"] = ollama_base_url
        if temperature is not None:
            updates["temperature"] = temperature
        if max_tokens is not None:
            updates["max_tokens"] = max_tokens
        
        if updates:
            svc.update_config(**updates)
        
        return {
            "success": True,
            "updated": list(updates.keys()),
            "current_config": {
                "default_provider": svc.config.default_provider,
                "default_model": svc.config.default_model,
                "ollama_base_url": svc.config.ollama_base_url,
                "temperature": svc.config.temperature,
                "max_tokens": svc.config.max_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Config update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== OpenAI-Compatible Proxy Endpoints ==============
# These provide drop-in OpenAI SDK compatibility

@router.post("/v1/chat/completions")
async def openai_compatible_chat(request: Request):
    """
    OpenAI-compatible chat completions endpoint.
    
    Drop-in replacement for OpenAI SDK - just change the base_url:
    ```python
    from openai import OpenAI
    client = OpenAI(base_url="http://localhost:7777/api/v1/litellm/v1", api_key="any")
    response = client.chat.completions.create(
        model="ollama/llama3.2",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    ```
    """
    try:
        body = await request.json()
        
        from services.litellm_service import get_litellm_service
        svc = get_litellm_service()
        
        messages = body.get("messages", [])
        model = body.get("model", svc.config.default_model)
        stream = body.get("stream", False)
        
        kwargs = {}
        for key in ["temperature", "max_tokens", "top_p", "tools", "tool_choice", "response_format"]:
            if key in body:
                kwargs[key] = body[key]
        
        if stream:
            response = await svc.achat_completion(
                messages=messages,
                model=model,
                stream=True,
                **kwargs
            )
            return StreamingResponse(
                _openai_stream_response(response, model),
                media_type="text/event-stream"
            )
        
        response = await svc.achat_completion(
            messages=messages,
            model=model,
            stream=False,
            **kwargs
        )
        
        # Return in OpenAI format
        return response.model_dump()
        
    except Exception as e:
        logger.error(f"OpenAI-compatible chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _openai_stream_response(response, model: str):
    """Generate OpenAI-compatible SSE stream."""
    import json
    import time
    
    try:
        async for chunk in response:
            chunk_dict = chunk.model_dump()
            yield f"data: {json.dumps(chunk_dict)}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_chunk = {
            "error": {
                "message": str(e),
                "type": "server_error"
            }
        }
        yield f"data: {json.dumps(error_chunk)}\n\n"
