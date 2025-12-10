"""
Unit tests for Tool Service and MCP Client.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.tool_service import ToolService
from services.mcp_client import MCPClient


class TestToolService:
    """Test the Tool Service."""
    
    @pytest.fixture
    def tool_service(self):
        """Create a tool service instance for testing."""
        service = ToolService()
        return service
    
    def test_tool_service_initialization(self, tool_service):
        """Test tool service initializes correctly."""
        assert tool_service is not None
        assert hasattr(tool_service, 'available_tools')
    
    def test_register_tool(self, tool_service):
        """Test registering a new tool."""
        def test_tool(param: str) -> str:
            return f"Processed {param}"
        
        tool_service.register_tool("test_tool", test_tool, "A test tool")
        
        assert "test_tool" in tool_service.available_tools
        assert tool_service.available_tools["test_tool"]["function"] == test_tool
    
    def test_execute_tool(self, tool_service):
        """Test executing a registered tool."""
        def test_tool(param: str) -> str:
            return f"Result: {param}"
        
        tool_service.register_tool("test_tool", test_tool, "A test tool")
        result = tool_service.execute_tool("test_tool", param="test")
        
        assert result == "Result: test"
    
    def test_execute_nonexistent_tool(self, tool_service):
        """Test executing a tool that doesn't exist."""
        with pytest.raises(KeyError):
            tool_service.execute_tool("nonexistent_tool")
    
    def test_list_tools(self, tool_service):
        """Test listing all available tools."""
        def tool1(x: str) -> str:
            return x
        
        def tool2(y: int) -> int:
            return y
        
        tool_service.register_tool("tool1", tool1, "First tool")
        tool_service.register_tool("tool2", tool2, "Second tool")
        
        tools = tool_service.list_tools()
        
        assert len(tools) >= 2
        assert "tool1" in tools
        assert "tool2" in tools


class TestMCPClient:
    """Test the MCP Client."""
    
    @pytest.fixture
    def mcp_client(self):
        """Create an MCP client instance for testing."""
        client = MCPClient()
        return client
    
    def test_mcp_client_initialization(self, mcp_client):
        """Test MCP client initializes correctly."""
        assert mcp_client is not None
    
    @pytest.mark.asyncio
    async def test_connect_to_server(self, mcp_client):
        """Test connecting to an MCP server."""
        with patch.object(mcp_client, '_establish_connection') as mock_connect:
            mock_connect.return_value = AsyncMock()
            
            await mcp_client.connect("test-server", "http://localhost:8080")
            
            assert "test-server" in mcp_client.servers
    
    @pytest.mark.asyncio
    async def test_list_server_tools(self, mcp_client):
        """Test listing tools from an MCP server."""
        with patch.object(mcp_client, 'servers') as mock_servers:
            mock_server = AsyncMock()
            mock_server.list_tools = AsyncMock(return_value=[
                {"name": "tool1", "description": "First tool"},
                {"name": "tool2", "description": "Second tool"}
            ])
            mock_servers.__getitem__.return_value = mock_server
            
            tools = await mcp_client.list_tools("test-server")
            
            assert len(tools) == 2
            assert tools[0]["name"] == "tool1"
    
    @pytest.mark.asyncio
    async def test_call_server_tool(self, mcp_client):
        """Test calling a tool on an MCP server."""
        with patch.object(mcp_client, 'servers') as mock_servers:
            mock_server = AsyncMock()
            mock_server.call_tool = AsyncMock(return_value={"result": "success"})
            mock_servers.__getitem__.return_value = mock_server
            
            result = await mcp_client.call_tool(
                "test-server",
                "test_tool",
                {"param": "value"}
            )
            
            assert result["result"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
