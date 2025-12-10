from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from services.llm_service import get_llm_service
from sources.logger import Logger

router = APIRouter()
logger = Logger("models_router.log")

@router.get("/models", response_model=List[str])
async def list_models(provider: Optional[str] = Query(None, description="Filter models by provider")):
    """
    List available models. 
    If provider is specified, returns models for that provider.
    Otherwise returns models for the currently active provider.
    """
    try:
        llm_service = get_llm_service()
        models = llm_service.get_available_models(provider)
        return models
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
