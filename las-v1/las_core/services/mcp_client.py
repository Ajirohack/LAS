import asyncio
import aiohttp
from typing import List, Dict, Any
from sources.logger import Logger
from config.settings import settings

logger = Logger("mcp_client.log")

class MCPClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPClient, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.servers = {} # name -> url
        # Load configured servers from settings or DB
        # self.connect_to_server("filesystem", "http://localhost:8001")

    async def connect_to_server(self, name: str, url: str):
        """Connect to an MCP server."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/mcp/v1/initialize") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.servers[name] = {
                            "url": url,
                            "capabilities": data.get("capabilities", {}),
                            "tools": data.get("tools", [])
                        }
                        logger.info(f"Connected to MCP server: {name} at {url}")
                        return True
                    else:
                        logger.error(f"Failed to connect to MCP server {name}: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error connecting to MCP server {name}: {e}")
            return False

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List tools available on a specific MCP server."""
        if server_name not in self.servers:
            return []
        return self.servers[server_name]["tools"]

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        """Call a tool on an MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not connected")
        
        url = self.servers[server_name]["url"]
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    },
                    "id": 1
                }
                async with session.post(f"{url}/mcp/v1/message", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result")
                    else:
                        raise Exception(f"MCP tool call failed: {response.status}")
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise e

def get_mcp_client():
    return MCPClient()
