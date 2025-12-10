from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from plugins.plugin_manager import get_plugin_manager

router = APIRouter()

class InstallRequest(BaseModel):
    source: str
    name: str = None

@router.get("/")
async def list_plugins():
    """List all discovered plugins."""
    try:
        manager = get_plugin_manager()
        plugins = manager.discover_plugins()
        return {
            "plugins": [
                {
                    "name": p.manifest.name,
                    "version": p.manifest.version,
                    "author": p.manifest.author,
                    "description": p.manifest.description,
                    "loaded": p.loaded,
                    "enabled": p.enabled,
                    "error": p.error
                }
                for p in plugins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")

@router.get("/{plugin_name}")
async def get_plugin_details(plugin_name: str):
    """Get detailed information about a plugin."""
    try:
        manager = get_plugin_manager()
        # Find plugin
        plugins = manager.discover_plugins()
        plugin_info = next((p for p in plugins if p.manifest.name == plugin_name), None)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_name}' not found")
        
        return plugin_info.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get plugin details: {str(e)}")

@router.post("/load/{plugin_name}")
async def load_plugin(plugin_name: str):
    """Load a plugin."""
    try:
        manager = get_plugin_manager()
        result = manager.load_plugin(plugin_name)
        
        if not result or result.error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load plugin: {result.error if result else 'Not found'}"
            )
        
        return {"status": "loaded", "plugin": plugin_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load plugin: {str(e)}")

@router.post("/install")
async def install_plugin(request: InstallRequest):
    """Install a plugin from a source."""
    try:
        manager = get_plugin_manager()
        success = manager.install_plugin(request.source, request.name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Plugin installation failed")
        
        return {"status": "installed", "source": request.source}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to install plugin: {str(e)}")
