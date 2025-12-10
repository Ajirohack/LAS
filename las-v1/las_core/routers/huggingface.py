"""
HuggingFace Hub Router - API endpoints for HuggingFace services.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.responses import FileResponse

from services.huggingface_service import get_huggingface_service

router = APIRouter()

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "meta-llama/Llama-3.3-70B-Instruct"
    max_tokens: int = 1024
    temperature: float = 0.7

class TextGenerationRequest(BaseModel):
    prompt: str
    model: str = "meta-llama/Llama-3.3-70B-Instruct"
    max_new_tokens: int = 512

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: str = "stabilityai/stable-diffusion-3.5-large"
    negative_prompt: Optional[str] = None

class EmbeddingRequest(BaseModel):
    texts: List[str]
    model: str = "sentence-transformers/all-MiniLM-L6-v2"

@router.post("/hf/chat")
async def hf_chat(request: ChatRequest):
    """Chat with HuggingFace LLMs."""
    try:
        hf_service = get_huggingface_service()
        response = hf_service.chat_completion(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/generate")
async def hf_generate(request: TextGenerationRequest):
    """Generate text with HuggingFace models."""
    try:
        hf_service = get_huggingface_service()
        text = hf_service.text_generation(
            prompt=request.prompt,
            model=request.model,
            max_new_tokens=request.max_new_tokens
        )
        return {"generated_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/text-to-image")
async def hf_text_to_image(request: ImageGenerationRequest):
    """Generate images with HuggingFace models."""
    try:
        hf_service = get_huggingface_service()
        image_path = hf_service.text_to_image(
            prompt=request.prompt,
            model=request.model,
            negative_prompt=request.negative_prompt
        )
        return {"image_path": image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/image-classification")
async def hf_image_classification(
    file: UploadFile = File(...),
    model: str = Form("google/vit-base-patch16-224")
):
    """Classify image content."""
    try:
        import tempfile
        import os
        
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hf_service = get_huggingface_service()
            results = hf_service.image_classification(tmp_path, model=model)
            return {"classifications": results}
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/object-detection")
async def hf_object_detection(
    file: UploadFile = File(...),
    model: str = Form("facebook/detr-resnet-50")
):
    """Detect objects in image."""
    try:
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hf_service = get_huggingface_service()
            results = hf_service.object_detection(tmp_path, model=model)
            return {"detections": results}
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/embeddings")
async def hf_embeddings(request: EmbeddingRequest):
    """Generate text embeddings."""
    try:
        hf_service = get_huggingface_service()
        embeddings = hf_service.feature_extraction(
            texts=request.texts,
            model=request.model
        )
        return {"embeddings": embeddings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hf/models")
async def hf_search_models(
    task: Optional[str] = None,
    library: Optional[str] = None,
    limit: int = 20
):
    """Search HuggingFace Hub for models."""
    try:
        hf_service = get_huggingface_service()
        models = hf_service.search_models(
            task=task,
            library=library,
            limit=limit
        )
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hf/models/{model_id:path}")
async def hf_get_model_info(model_id: str):
    """Get detailed model information."""
    try:
        hf_service = get_huggingface_service()
        info = hf_service.get_model_info(model_id)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hf/speech-to-text")
async def hf_speech_to_text(
    file: UploadFile = File(...),
    model: str = Form("openai/whisper-large-v3")
):
    """Transcribe audio to text."""
    try:
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            hf_service = get_huggingface_service()
            text = hf_service.speech_to_text(tmp_path, model=model)
            return {"text": text}
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
