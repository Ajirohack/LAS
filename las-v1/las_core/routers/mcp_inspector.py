from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.mcp_server import get_mcp_server
from services.mcp_discovery import get_mcp_discovery

router = APIRouter()

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

@router.get("/info")
async def get_server_info():
    """Get MCP server information."""
    server = get_mcp_server()
    return server.get_server_info()

@router.get("/tools")
async def list_tools():
    """List all available MCP tools."""
    server = get_mcp_server()
    return {"tools": server.list_tools()}

@router.post("/call")
async def call_tool(request: ToolCallRequest):
    """Call an MCP tool."""
    server = get_mcp_server()
    result = server.call_tool(request.tool_name, request.arguments)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result

@router.get("/servers")
async def discover_servers():
    """Discover available MCP servers."""
    discovery = get_mcp_discovery()
    servers = discovery.discover_all()
    return {"servers": servers}

@router.get("/servers/{server_name}/tools")
async def get_server_tools(server_name: str):
    """Get tools from a specific MCP server."""
    discovery = get_mcp_discovery()
    servers = discovery.discover_all()
    
    server = next((s for s in servers if s["name"] == server_name), None)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
    
    tools = discovery.get_tools(server)
    return {"tools": tools}

@router.get("/servers/{server_name}/health")
async def check_server_health(server_name: str):
    """Check health of a specific MCP server."""
    discovery = get_mcp_discovery()
    servers = discovery.discover_all()
    
    server = next((s for s in servers if s["name"] == server_name), None)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
    
    healthy = discovery.health_check(server)
    return {"server": server_name, "healthy": healthy}
