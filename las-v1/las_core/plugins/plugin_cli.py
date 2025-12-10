#!/usr/bin/env python3
"""
LAS Plugin CLI Tool

Usage:
    las-plugin create <name>        Create a new plugin scaffold
    las-plugin list                  List installed plugins
    las-plugin install <source>      Install a plugin
"""

import sys
import json
from pathlib import Path
from datetime import datetime

PLUGIN_TEMPLATE = """# {name} Plugin

## Description
{description}

## Installation
Copy this directory to `plugins/{name}/` in your LAS installation.

## Configuration
Edit `manifest.json` to configure permissions and metadata.
"""

MANIFEST_TEMPLATE = {{
    "name": "{name}",
    "version": "0.1.0",
    "author": "{author}",
    "description": "{description}",
    "license": "MIT",
    "permissions": {{
        "file_system": False,
        "network": False,
        "database": False,
        "tools": []
    }},
    "metadata": {{
        "entry_point": "{name}.main",
        "dependencies": [],
        "worker_class": None,
        "tool_class": None
    }},
    "created_at": "{timestamp}",
    "updated_at": "{timestamp}"
}}

MAIN_MODULE_TEMPLATE = """\"\"\"
{name} Plugin - Main Module
\"\"\"

def initialize():
    \"\"\"Initialize the plugin.\"\"\"
    print("Plugin '{name}' initialized")

def cleanup():
    \"\"\"Cleanup on plugin unload.\"\"\"
    print("Plugin '{name}' cleaned up")

# Optional: Define a custom worker
class {class_name}Worker:
    def __init__(self):
        self.name = "{name}"
    
    def run(self, state):
        # Implement your worker logic here
        return {{"messages": [], "status": "completed"}}

# Optional: Define a custom tool
class {class_name}Tool:
    name = "{name}_tool"
    description = "Tool from {name} plugin"
    
    def execute(self, *args, **kwargs):
        # Implement your tool logic here
        return "Tool executed successfully"
"""

def create_plugin(name: str, description: str = "", author: str = "Anonymous"):
    """Create a new plugin scaffold."""
    plugin_dir = Path(name)
    
    if plugin_dir.exists():
        print(f"Error: Directory '{name}' already exists")
        return False
    
    # Create directory structure
    plugin_dir.mkdir(parents=True)
    (plugin_dir / name).mkdir()
    
    # Create README
    readme_content = PLUGIN_TEMPLATE.format(
        name=name,
        description=description or f"Plugin: {name}"
    )
    (plugin_dir / "README.md").write_text(readme_content)
    
    # Create manifest.json
    timestamp = datetime.now().isoformat()
    manifest_content = MANIFEST_TEMPLATE.format(
        name=name,
        author=author,
        description=description or f"Plugin: {name}",
        timestamp=timestamp
    )
    (plugin_dir / "manifest.json").write_text(manifest_content)
    
    # Create main module
    class_name = "".join(word.capitalize() for word in name.split("_"))
    main_content = MAIN_MODULE_TEMPLATE.format(
        name=name,
        class_name=class_name
    )
    (plugin_dir / name / "main.py").write_text(main_content)
    (plugin_dir / name / "__init__.py").write_text("")
    
    print(f"✓ Plugin '{name}' created successfully!")
    print(f"  Directory: {plugin_dir.absolute()}")
    print(f"\\nNext steps:")
    print(f"  1. Edit {plugin_dir}/manifest.json to configure permissions")
    print(f"  2. Implement your logic in {plugin_dir}/{name}/main.py")
    print(f"  3. Install with: las-plugin install {plugin_dir.absolute()}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Usage: las-plugin create <name>")
            sys.exit(1)
        
        name = sys.argv[2]
        description = input(f"Description for '{name}': ").strip()
        author = input("Author name: ").strip() or "Anonymous"
        
        create_plugin(name, description, author)
    
    elif command == "list":
        print("Listing plugins functionality requires LAS backend API")
        print("Use: curl http://localhost:7777/api/plugins")
    
    elif command == "install":
        if len(sys.argv) < 3:
            print("Usage: las-plugin install <source>")
            sys.exit(1)
        
        print("Install functionality requires LAS backend API")
        print(f"Use: curl -X POST http://localhost:7777/api/plugins/install -d '{{'source': '{sys.argv[2]}'}}'")
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
