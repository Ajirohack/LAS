from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class PluginPermissions(BaseModel):
    """Permissions required by a plugin."""
    file_system: bool = False
    network: bool = False
    database: bool = False
    tools: List[str] = []  # List of tool names the plugin can access

class PluginMetadata(BaseModel):
    """Plugin metadata and entry points."""
    entry_point: str = Field(..., description="Python module path (e.g., 'my_plugin.main')")
    dependencies: List[str] = Field(default_factory=list, description="Python package dependencies")
    worker_class: Optional[str] = None  # For agent worker plugins
    tool_class: Optional[str] = None    # For tool plugins

class PluginManifest(BaseModel):
    """Standard plugin manifest (manifest.json)."""
    name: str = Field(..., description="Unique plugin name")
    version: str = Field(..., description="Semantic version (e.g., '1.0.0')")
    author: str
    description: str
    homepage: Optional[str] = None
    license: str = "MIT"
    
    permissions: PluginPermissions
    metadata: PluginMetadata
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PluginInfo(BaseModel):
    """Runtime plugin information."""
    manifest: PluginManifest
    installed_path: str
    loaded: bool = False
    enabled: bool = True
    error: Optional[str] = None
