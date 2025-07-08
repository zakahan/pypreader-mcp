import pytest
from fastmcp import Client
from pypreader_mcp.server import mcp as server


@pytest.fixture
def mcp_server():
    return server


async def test_tool_functionality(mcp_server):
    # Pass the server directly to the Client constructor
    async with Client(mcp_server) as client:
        result = await client.list_tools()
        assert len(result) > 0
