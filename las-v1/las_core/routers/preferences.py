from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.db import get_preference, set_preference, get_all_preferences
from database.models import UserPreference, ModelSelection, PreferencesResponse
from sources.logger import Logger

router = APIRouter(prefix="/preferences", tags=["preferences"])
logger = Logger("preferences_router.log")

@router.get("", response_model=PreferencesResponse)
async def get_all_prefs():
    """Get all user preferences."""
    try:
        prefs = get_all_preferences()
        return PreferencesResponse(preferences=prefs)
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{key}")
async def get_pref(key: str):
    """Get a specific preference by key."""
    try:
        value = get_preference(key)
        if value is None:
            raise HTTPException(status_code=404, detail=f"Preference '{key}' not found")
        return {"key": key, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preference {key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("")
async def set_pref(pref: UserPreference):
    """Set or update a preference."""
    try:
        set_preference(pref.key, pref.value)
        return {"success": True, "key": pref.key, "value": pref.value}
    except Exception as e:
        logger.error(f"Error setting preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-selection", response_model=ModelSelection)
async def get_model_selection():
    """Get the saved model selection."""
    try:
        provider = get_preference("selected_provider") or "ollama"
        model = get_preference("selected_model") or "tinydolphin"
        base_url = get_preference("ollama_base_url")
        
        return ModelSelection(provider=provider, model=model, base_url=base_url)
    except Exception as e:
        logger.error(f"Error getting model selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/model-selection")
async def save_model_selection(selection: ModelSelection):
    """Save the model selection."""
    try:
        set_preference("selected_provider", selection.provider)
        set_preference("selected_model", selection.model)
        if selection.base_url:
            set_preference("ollama_base_url", selection.base_url)
        
        logger.info(f"Model selection saved: {selection.provider}/{selection.model}")
        return {"success": True, "selection": selection}
    except Exception as e:
        logger.error(f"Error saving model selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/theme")
async def get_theme_preference():
    """Get the saved theme preference."""
    try:
        theme = get_preference("theme") or "dark"
        custom_theme = get_preference("custom_theme")
        
        return {
            "theme": theme,
            "custom_theme": custom_theme
        }
    except Exception as e:
        logger.error(f"Error getting theme preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/theme")
async def save_theme_preference(theme: str, custom_theme: dict = None):
    """Save the theme preference."""
    try:
        set_preference("theme", theme)
        if custom_theme:
            set_preference("custom_theme", custom_theme)
        
        logger.info(f"Theme preference saved: {theme}")
        return {"success": True, "theme": theme}
    except Exception as e:
        logger.error(f"Error saving theme preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))
