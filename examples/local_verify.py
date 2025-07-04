import os
import time
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

        print("> 3. get_source_code_by_symbol:")
        start_time = time.time()
        result = await client.call_tool(
            name="get_source_code_by_symbol",
            arguments={
                "package_name": "fastmcp",
                "symbol_name": "MCPError",
            },
        )
        end_time = time.time()
        print(result)
        print(f"Duration consumed: {1000 * (end_time - start_time)} ms")


if __name__ == "__main__":
    asyncio.run(main())
