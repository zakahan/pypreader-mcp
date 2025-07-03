import os
import asyncio
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

transport = StdioTransport(
    command="python",
    args=[
        "-m",
        "pypreader_mcp.server",
    ],
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)


async def main():
    # Connect via stdio to a local script
    async with Client(transport) as client:
        print("> 1. List tools:")
        result = await client.list_tools()
        for tool in result:
            print(tool)
        print("> 2. get_package:")
        result = await client.call_tool(
            name="get_package_directory", arguments={"package_name": "fastmcp"}
        )
        print(result)
        print("> 3. get_symbol_definition:")
        result = await client.call_tool(
            name="get_symbol_definition",
            arguments={"package_name": "mcp.types", "symbol_name": "CallToolResult"},
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
