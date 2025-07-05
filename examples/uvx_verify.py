import sys
import asyncio
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport


transport = UvxStdioTransport(
    from_package="git+https://github.com/zakahan/pypreader-mcp.git",
    tool_name="pypreader-mcp",
    env_vars={
        "CURRENT_PYTHON_PATH": sys.executable,
        "CURRENT_LOGGING_LEVEL": "ERROR",
    },
)


async def main():
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
        result = await client.call_tool(
            name="get_source_code_by_symbol",
            arguments={"package_name": "mcp.types", "symbol_name": "CallToolResult"},
        )
        print(result)


if __name__ == "__main__":
    # uvx --from git+https://github.com/zakahan/pypreader-mcp.git pypreader-mcp --python_path xxxxx --logging_level ERROR
    asyncio.run(main())
