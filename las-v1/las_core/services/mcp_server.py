"""
MCP Server Mode - Expose LAS tools to other applications via MCP protocol.
"""

from typing import Dict, List, Any, Optional, Callable
import json
import asyncio

class MCPServer:
    """
    MCP Server implementation to expose LAS capabilities as MCP tools.
    Allows other applications to call LAS functions via the MCP protocol.
    """
    
    def __init__(self, name: str = "las-server"):
        self.name = name
        self.tools: Dict[str, Callable] = {}
        self.resources: Dict[str, Any] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register LAS's default tools for MCP exposure."""
        
        # Query tool
        self.register_tool(
            name="query",
            description="Send a query to the LAS agent",
            parameters={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Query text"},
                    "provider": {"type": "string", "description": "LLM provider"},
                    "model": {"type": "string", "description": "Model name"}
                },
                "required": ["text"]
            },
            handler=self._handle_query
        )
        
        # Memory tools
        self.register_tool(
            name="list_skills",
            description="List all saved skills",
            parameters={"type": "object", "properties": {}},
            handler=self._handle_list_skills
        )
        
        self.register_tool(
            name="get_lessons",
            description="Get lessons learned for a task",
            parameters={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string", "description": "Task description"}
                },
                "required": ["task_description"]
            },
            handler=self._handle_get_lessons
        )
        
        # Vision tool
        self.register_tool(
            name="analyze_image",
            description="Analyze an image with vision model",
            parameters={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to image"},
                    "prompt": {"type": "string", "description": "Analysis prompt"}
                },
                "required": ["image_path"]
            },
            handler=self._handle_analyze_image
        )
    
    def register_tool(self, name: str, description: str, 
                     parameters: Dict[str, Any], handler: Callable):
        """Register a tool for MCP exposure."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": parameters,
            "handler": handler
        }
    
    def _handle_query(self, **kwargs) -> Dict[str, Any]:
        """Handle query tool call."""
        # In production, this would call the actual LAS API
        text = kwargs.get("text")
        return {"result": f"Query received: {text}", "status": "success"}
    
    def _handle_list_skills(self, **kwargs) -> Dict[str, Any]:
        """Handle list_skills tool call."""
        from agents.memory.skill_manager import SkillManager
        manager = SkillManager()
        skills = manager.list_skills()
        return {"skills": skills, "status": "success"}
    
    def _handle_get_lessons(self, **kwargs) -> Dict[str, Any]:
        """Handle get_lessons tool call."""
        from agents.memory.reflection_manager import ReflectionManager
        manager = ReflectionManager()
        task_desc = kwargs.get("task_description", "")
        lessons = manager.get_lessons_for_task(task_desc)
        return {"lessons": lessons, "status": "success"}
    
    def _handle_analyze_image(self, **kwargs) -> Dict[str, Any]:
        """Handle analyze_image tool call."""
        from services.vision_service import get_vision_service
        vision = get_vision_service()
        image_path = kwargs.get("image_path")
        prompt = kwargs.get("prompt", "Describe this image")
        
        try:
            result = vision.analyze_image(image_path, prompt)
            return {"analysis": result, "status": "success"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found", "status": "error"}
        
        tool = self.tools[tool_name]
        handler = tool["handler"]
        
        try:
            result = handler(**arguments)
            return result
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.name,
            "version": "0.1.0",
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True}
            }
        }

# Create singleton instance
_mcp_server: Optional[MCPServer] = None

def get_mcp_server() -> MCPServer:
    """Get or create MCP Server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
