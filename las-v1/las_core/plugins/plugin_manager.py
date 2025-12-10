import json
import importlib
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from .plugin_schema import PluginManifest, PluginInfo, PluginPermissions

class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_plugins: Dict[str, PluginInfo] = {}
    
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover all plugins in the plugins directory."""
        discovered = []
        
        for plugin_path in self.plugins_dir.iterdir():
            if not plugin_path.is_dir():
                continue
            
            manifest_file = plugin_path / "manifest.json"
            if not manifest_file.exists():
                continue
            
            try:
                manifest = self.load_manifest(manifest_file)
                plugin_info = PluginInfo(
                    manifest=manifest,
                    installed_path=str(plugin_path)
                )
                discovered.append(plugin_info)
            except Exception as e:
                print(f"Failed to load plugin at {plugin_path}: {e}")
        
        return discovered
    
    def load_manifest(self, manifest_path: Path) -> PluginManifest:
        """Load and validate a plugin manifest."""
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        return PluginManifest(**data)
    
    def validate_manifest(self, manifest: PluginManifest) -> bool:
        """Validate plugin manifest."""
        # Check required fields
        if not manifest.name or not manifest.version:
            return False
        
        # Validate entry point format
        if not manifest.metadata.entry_point:
            return False
        
        return True
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginInfo]:
        """Load a plugin by name."""
        # Check if already loaded
        if plugin_name in self.loaded_plugins:
            return self.loaded_plugins[plugin_name]
        
        # Find plugin
        plugin_info = None
        for info in self.discover_plugins():
            if info.manifest.name == plugin_name:
                plugin_info = info
                break
        
        if not plugin_info:
            print(f"Plugin '{plugin_name}' not found")
            return None
        
        # Validate
        if not self.validate_manifest(plugin_info.manifest):
            plugin_info.error = "Invalid manifest"
            return plugin_info
        
        try:
            # Add plugin path to sys.path
            plugin_path = Path(plugin_info.installed_path)
            if str(plugin_path) not in sys.path:
                sys.path.insert(0, str(plugin_path))
            
            # Import entry point
            entry_point = plugin_info.manifest.metadata.entry_point
            module = importlib.import_module(entry_point)
            
            # Mark as loaded
            plugin_info.loaded = True
            self.loaded_plugins[plugin_name] = plugin_info
            
            print(f"✓ Plugin '{plugin_name}' loaded successfully")
            return plugin_info
        
        except Exception as e:
            plugin_info.error = str(e)
            plugin_info.loaded = False
            print(f"Failed to load plugin '{plugin_name}': {e}")
            return plugin_info
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name in self.loaded_plugins:
            # Remove from sys.modules
            entry_point = self.loaded_plugins[plugin_name].manifest.metadata.entry_point
            if entry_point in sys.modules:
                del sys.modules[entry_point]
            
            del self.loaded_plugins[plugin_name]
            print(f"✓ Plugin '{plugin_name}' unloaded")
            return True
        return False
    
    def list_loaded(self) -> List[str]:
        """List loaded plugin names."""
        return list(self.loaded_plugins.keys())
    
    def install_plugin(self, source: str, name: Optional[str] = None) -> bool:
        """
        Install a plugin from a source (URL, git repo, or local path).
        
        Args:
            source: URL, git repo, or local path to plugin
            name: Optional plugin name (used for directory)
        
        Returns:
            Success boolean
        """
        try:
            source_path = Path(source)
            
            # Handle local path
            if source_path.exists():
                # Copy to plugins directory
                import shutil
                target_name = name or source_path.name
                target_path = self.plugins_dir / target_name
                
                if target_path.exists():
                    print(f"Plugin '{target_name}' already exists")
                    return False
                
                shutil.copytree(source_path, target_path)
                print(f"✓ Plugin installed to {target_path}")
                return True
            
            # TODO: Handle URL and git sources
            print(f"Remote plugin installation not yet implemented: {source}")
            return False
        
        except Exception as e:
            print(f"Plugin installation failed: {e}")
            return False

# Create singleton instance
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager() -> PluginManager:
    """Get or create PluginManager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
