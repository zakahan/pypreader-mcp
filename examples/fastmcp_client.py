# uvx --from git+https://github.com/zakahan/pypreader-mcp.git pypreader-mcp

import asyncio
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport


transport = UvxStdioTransport(
    from_package="git+https://github.com/zakahan/pypreader-mcp.git",
    tool_name="pypreader-mcp"
)   

async def main():
    async with Client(transport) as client:
        result = await client.list_tools()
        for tool in result:
            print(tool)


if __name__ == "__main__":
    asyncio.run(main())