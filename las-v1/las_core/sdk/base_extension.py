from typing import Dict, Any, Callable

class BaseExtension:
    """
    Base class for all LAS extensions.
    Inherit from this class to create custom tools.
    """
    def __init__(self):
        self.commands: Dict[str, Callable] = {}

    def register_command(self, name: str, func: Callable):
        """
        Manually register a command.
        """
        self.commands[name] = func
