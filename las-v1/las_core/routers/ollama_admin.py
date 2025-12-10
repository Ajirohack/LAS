from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio
from ollama import Client
from sources.logger import Logger
from config.settings import settings

router = APIRouter(prefix="/ollama", tags=["ollama-admin"])
logger = Logger("ollama_admin.log")

class PullModelRequest(BaseModel):
    model: str
    insecure: Optional[bool] = False

class ModelInfo(BaseModel):
    name: str
    model: str
    size: int
    digest: str
    modified_at: str
    details: Optional[Dict[str, Any]] = None

class OllamaLibraryModel(BaseModel):
    name: str
    description: str
    tags: List[str]

def get_ollama_client():
    """Get Ollama client instance."""
    ollama_url = settings.provider_server_address if settings.provider_name == "ollama" else "http://localhost:11434"
    return Client(host=ollama_url)

@router.get("/models/local")
async def list_local_models():
    """
    List all locally downloaded Ollama models.
    Returns detailed information about each model.
    """
    try:
        client = get_ollama_client()
        models_response = client.list()
        
        models = []
        for model in models_response.get('models', []):
            models.append({
                "name": model.get('name'),
                "model": model.get('model', model.get('name')),
                "size": model.get('size', 0),
                "digest": model.get('digest', ''),
                "modified_at": model.get('modified_at', ''),
                "details": model.get('details', {})
            })
        
        logger.info(f"Listed {len(models)} local models")
        return {"models": models, "count": len(models)}
        
    except Exception as e:
        logger.error(f"Failed to list local models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{model_name}/info")
async def get_model_info(model_name: str):
    """
    Get detailed information about a specific model.
    """
    try:
        client = get_ollama_client()
        info = client.show(model_name)
        logger.info(f"Retrieved info for model: {model_name}")
        return info
        
    except Exception as e:
        logger.error(f"Failed to get model info for {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Model not found or error: {str(e)}")

@router.delete("/models/{model_name}")
async def delete_model(model_name: str):
    """
    Delete a local model.
    """
    try:
        client = get_ollama_client()
        client.delete(model_name)
        logger.info(f"Deleted model: {model_name}")
        return {"success": True, "message": f"Model '{model_name}' deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/models/pull")
async def pull_model(request: PullModelRequest):
    """
    Pull/download a model from Ollama registry with streaming progress.
    Returns a Server-Sent Events (SSE) stream with download progress.
    """
    async def progress_stream():
        try:
            client = get_ollama_client()
            logger.info(f"Starting pull for model: {request.model}")
            
            # Stream the pull progress
            for progress in client.pull(request.model, stream=True, insecure=request.insecure):
                # Format the progress data
                event_data = {
                    "status": progress.get('status', 'downloading'),
                    "digest": progress.get('digest', ''),
                    "total": progress.get('total', 0),
                    "completed": progress.get('completed', 0),
                }
                
                # Calculate percentage if available
                if event_data['total'] > 0:
                    event_data['percent'] = (event_data['completed'] / event_data['total']) * 100
                
                # Send as SSE event
                yield f"data: {json.dumps(event_data)}\n\n"
                await asyncio.sleep(0.1)  # Small delay to prevent overwhelming the client
            
            # Send completion event
            yield f"data: {json.dumps({'status': 'done', 'message': f'Model {request.model} pulled successfully'})}\n\n"
            logger.info(f"Successfully pulled model: {request.model}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to pull model {request.model}: {error_msg}")
            yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"
    
    return StreamingResponse(
        progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

import httpx
from bs4 import BeautifulSoup

# Cache for library models to avoid frequent scraping
_library_cache = {
    "data": [],
    "timestamp": 0
}
CACHE_TTL = 3600  # 1 hour

async def fetch_ollama_library():
    """
    Scrape popular models from ollama.com/library
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://ollama.com/library", timeout=10.0)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Ollama library: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            models = []
            
            # Find all model items (usually in a list or grid)
            # This selector might need adjustment based on Ollama's actual HTML structure
            # Based on typical structure: look for links to /library/modelname
            
            # Attempt to find model cards
            # Ollama library usually has a list of items with titles and descriptions
            items = soup.find_all('li', class_=lambda x: x and 'flex' in x) 
            
            # Fallback: look for any links starting with /library/
            if not items:
                links = soup.find_all('a', href=lambda x: x and x.startswith('/library/'))
                seen_models = set()
                
                for link in links:
                    href = link.get('href')
                    name = href.replace('/library/', '')
                    if name in seen_models or '/' in name: # Skip sub-pages or duplicates
                        continue
                    
                    seen_models.add(name)
                    
                    # Try to find description in sibling or child elements
                    description = ""
                    desc_tag = link.find_next('p')
                    if desc_tag:
                        description = desc_tag.text.strip()
                    
                    models.append({
                        "name": name,
                        "description": description or f"Ollama model: {name}",
                        "tags": ["text", "general"]
                    })
            else:
                # If we found structured items (this part is speculative without seeing exact HTML)
                # We'll stick to the link-based fallback which is more robust for now
                pass

            return models if models else None

    except Exception as e:
        logger.error(f"Error scraping Ollama library: {e}")
        return None

@router.get("/models/library")
async def get_library_models():
    """
    Get available models from Ollama library.
    Dynamically scrapes ollama.com/library with fallback to hardcoded list.
    """
    import time
    
    # Check cache
    current_time = time.time()
    if _library_cache["data"] and (current_time - _library_cache["timestamp"] < CACHE_TTL):
        return {"models": _library_cache["data"], "count": len(_library_cache["data"]), "source": "cache"}

    # Hardcoded fallback list
    fallback_models = [
        {
            "name": "llama3.2",
            "description": "Meta's Llama 3.2 model with improved performance",
            "tags": ["text", "general", "meta"]
        },
        {
            "name": "llama3.1",
            "description": "Meta's Llama 3.1 model",
            "tags": ["text", "general", "meta"]
        },
        {
            "name": "gemma2",
            "description": "Google's Gemma 2 model",
            "tags": ["text", "general", "google"]
        },
        {
            "name": "mistral",
            "description": "Mistral AI's flagship model",
            "tags": ["text", "general", "mistral"]
        },
        {
            "name": "mixtral",
            "description": "Mixtral 8x7B mixture of experts",
            "tags": ["text", "general", "mistral", "moe"]
        },
        {
            "name": "codellama",
            "description": "Meta's Code Llama for code generation",
            "tags": ["code", "programming", "meta"]
        },
        {
            "name": "phi3",
            "description": "Microsoft's Phi-3 small language model",
            "tags": ["text", "small", "microsoft"]
        },
        {
            "name": "qwen2.5",
            "description": "Alibaba's Qwen 2.5 model",
            "tags": ["text", "general", "multilingual"]
        },
        {
            "name": "llama3.2-vision",
            "description": "Llama 3.2 with vision capabilities",
            "tags": ["vision", "multimodal", "meta"]
        },
        {
            "name": "tinydolphin",
            "description": "Small, efficient model for testing",
            "tags": ["text", "small", "efficient"]
        },
    ]

    # Attempt dynamic fetch
    scraped_models = await fetch_ollama_library()
    
    if scraped_models:
        logger.info(f"Successfully scraped {len(scraped_models)} models from Ollama library")
        _library_cache["data"] = scraped_models
        _library_cache["timestamp"] = current_time
        return {"models": scraped_models, "count": len(scraped_models), "source": "live"}
    
    logger.warning("Using fallback hardcoded library models")
    return {"models": fallback_models, "count": len(fallback_models), "source": "fallback"}

@router.get("/status")
async def get_ollama_status():
    """
    Check if Ollama service is running and accessible.
    """
    try:
        client = get_ollama_client()
        # Try to list models to verify connectivity
        client.list()
        return {
            "status": "online",
            "url": client._client.base_url if hasattr(client, '_client') else "unknown"
        }
    except Exception as e:
        logger.error(f"Ollama service not accessible: {e}")
        return {
            "status": "offline",
            "error": str(e)
        }

from fastapi import Request

@router.api_route("/api/{path:path}", methods=["GET", "POST", "DELETE", "PUT"])
async def proxy_ollama_api(path: str, request: Request):
    """
    Proxy requests to the underlying Ollama API.
    Allows accessing the raw Ollama API via /api/ollama/api/...
    """
    ollama_base_url = settings.provider_server_address if settings.provider_name == "ollama" else "http://localhost:11434"
    target_url = f"{ollama_base_url}/api/{path}"
    
    logger.info(f"Proxying request to Ollama: {request.method} {target_url}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Forward the request
            content = await request.body()
            headers = dict(request.headers)
            headers.pop("host", None) # Remove host header to avoid conflicts
            headers.pop("content-length", None) # Let httpx handle this
            
            response = await client.request(
                method=request.method,
                url=target_url,
                content=content,
                headers=headers,
                timeout=60.0
            )
            
            # Stream response if it's a streaming endpoint
            if response.headers.get("transfer-encoding") == "chunked" or path in ["generate", "chat", "pull", "push"]:
                return StreamingResponse(
                    response.aiter_bytes(),
                    status_code=response.status_code,
                    media_type=response.headers.get("content-type"),
                    background=None
                )
            else:
                return JSONResponse(
                    content=response.json() if response.headers.get("content-type") == "application/json" else response.text,
                    status_code=response.status_code
                )
                
    except Exception as e:
        logger.error(f"Failed to proxy to Ollama: {e}")
        raise HTTPException(status_code=500, detail=str(e))
