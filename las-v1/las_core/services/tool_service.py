import importlib
import os
import glob
import inspect
from typing import List, Dict, Any, Callable
from sources.logger import Logger
from config.settings import settings

logger = Logger("tool_service.log")

class ToolService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolService, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.extensions = {}
        self.commands = {}
        self.load_extensions()

    def load_extensions(self):
        """Dynamically load extensions from the extensions directory."""
        extensions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "extensions")
        extension_files = glob.glob(os.path.join(extensions_dir, "*.py"))

        for file_path in extension_files:
            module_name = os.path.basename(file_path)[:-3]
            if module_name == "__init__":
                continue

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find classes that end with 'Extension'
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and name.endswith("Extension"):
                        self.register_extension(name, obj)
            except Exception as e:
                logger.error(f"Failed to load extension {module_name}: {e}")

    def register_extension(self, name: str, extension_cls: Any):
        """Register an extension and its commands."""
        try:
            instance = extension_cls()
            self.extensions[name] = instance
            
            # 1. Register commands from 'commands' dict (Legacy/Manual)
            if hasattr(instance, "commands"):
                for cmd_name, cmd_func in instance.commands.items():
                    self.commands[cmd_name] = {
                        "function": cmd_func,
                        "extension": name,
                        "description": cmd_func.__doc__ or "No description"
                    }
                    logger.info(f"Registered command: {cmd_name} from {name}")

            # 2. Register commands decorated with @command (SDK)
            for attr_name in dir(instance):
                attr = getattr(instance, attr_name)
                if callable(attr) and getattr(attr, "_is_command", False):
                    cmd_name = getattr(attr, "_command_name")
                    description = getattr(attr, "_command_description")
                    
                    self.commands[cmd_name] = {
                        "function": attr,
                        "extension": name,
                        "description": description or "No description"
                    }
                    logger.info(f"Registered SDK command: {cmd_name} from {name}")

        except Exception as e:
            logger.error(f"Failed to register extension {name}: {e}")

    async def execute_command(self, command_name: str, **kwargs):
        """Execute a registered command."""
        if command_name not in self.commands:
            raise ValueError(f"Command {command_name} not found")

        cmd_info = self.commands[command_name]
        func = cmd_info["function"]
        
        try:
            # Check if function is async
            if inspect.iscoroutinefunction(func):
                return await func(**kwargs)
            else:
                return func(**kwargs)
        except Exception as e:
            logger.error(f"Error executing command {command_name}: {e}")
            raise e

    def get_available_commands(self) -> List[Dict[str, Any]]:
        """List all available commands."""
        return [
            {
                "name": name,
                "description": info["description"],
                "extension": info["extension"]
            }
            for name, info in self.commands.items()
        ]

def get_tool_service():
    return ToolService()
