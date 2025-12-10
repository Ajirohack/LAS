"""
MCP Discovery - Auto-discover MCP servers on localhost.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

class MCPDiscovery:
    """Discovers and manages MCP servers."""
    
    def __init__(self):
        self.discovered_servers: List[Dict[str, Any]] = []
        self.config_paths = [
            Path.home() / ".config" / "mcp" / "servers.json",
            Path.home() / ".mcp" / "servers.json",
            Path("/etc/mcp/servers.json")
        ]
    
    def discover_from_config(self) -> List[Dict[str, Any]]:
        """Discover MCP servers from config files."""
        servers = []
        
        for config_path in self.config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    if isinstance(config, dict) and "servers" in config:
                        for server_name, server_config in config["servers"].items():
                            servers.append({
                                "name": server_name,
                                "config": server_config,
                                "source": str(config_path)
                            })
                except Exception as e:
                    print(f"Failed to load MCP config from {config_path}: {e}")
        
        return servers
    
    def discover_from_ports(self, ports: List[int] = [3000, 3001, 8080, 8081]) -> List[Dict[str, Any]]:
        """Discover MCP servers by checking common ports."""
        servers = []
        
        for port in ports:
            url = f"http://localhost:{port}"
            try:
                # Try to get server info
                response = requests.get(f"{url}/mcp/info", timeout=1)
                if response.status_code == 200:
                    info = response.json()
                    servers.append({
                        "name": info.get("name", f"server-{port}"),
                        "url": url,
                        "port": port,
                        "version": info.get("version"),
                        "source": "port_scan"
                    })
            except:
                # Server not responding on this port
                pass
        
        return servers
    
    def discover_all(self) -> List[Dict[str, Any]]:
        """Discover all MCP servers (config + ports)."""
        servers = []
        
        # From config files
        config_servers = self.discover_from_config()
        servers.extend(config_servers)
        
        # From port scanning
        port_servers = self.discover_from_ports()
        servers.extend(port_servers)
        
        self.discovered_servers = servers
        return servers
    
    def health_check(self, server: Dict[str, Any]) -> bool:
        """Check if a server is healthy."""
        url = server.get("url")
        if not url:
            return False
        
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_tools(self, server: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tools from a discovered server."""
        url = server.get("url")
        if not url:
            return []
        
        try:
            response = requests.get(f"{url}/mcp/tools", timeout=2)
            if response.status_code == 200:
                return response.json().get("tools", [])
        except:
            pass
        
        return []

# Create singleton instance
_mcp_discovery: Optional[MCPDiscovery] = None

def get_mcp_discovery() -> MCPDiscovery:
    """Get or create MCP Discovery instance."""
    global _mcp_discovery
    if _mcp_discovery is None:
        _mcp_discovery = MCPDiscovery()
    return _mcp_discovery
