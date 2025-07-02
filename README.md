# pypreader-mcp

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python Package Reader server implementing the Model Context Protocol (MCP). This server allows Large Language Models (LLMs) and other AI agents to inspect the contents of Python packages within a specified environment.

## Overview

`pypreader-mcp` acts as a bridge between an AI model and a local Python environment. By exposing a set of tools through the Model Context Protocol, it enables the AI to programmatically browse installed packages, view their file structure, and read their source code. This is useful for tasks like code analysis, dependency inspection, and automated programming assistance.

## Features

The server provides the following tools to an MCP client:

-   `get_pypi_description(package_name: str)`: Fetches the official description of a package from PyPI.
-   `get_package_directory(package_name: str)`: Lists the entire file and directory structure of a specified installed package.
-   `get_source_code(package_path: str)`: Retrieves the full source code of a specific file within a package.

## Usage

This tool is designed to be used as an MCP server within an AI-powered environment like [Cursor](https://cursor.sh/) or [Trae](https://trae.ai/). It is not meant to be cloned and run manually.

### Configuration

In your AI environment's MCP server configuration, add a new server with the following settings. This allows the AI to use `uvx` to run the server directly from its Git repository.

```json
{
  "mcpServers": {
    "PypReader": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/zakahan/pypreader-mcp.git",
        "pypreader-mcp",
        "--python_path",
        "/path/to/your/project/.venv/bin/python" 
      ]
    }
  }
}
```

**Configuration Details**:

-   **`command`**: Should be `uvx`, which is a tool for running Python applications from various sources.
-   **`args`**: 
    -   `--from git+https://github.com/zakahan/pypreader-mcp.git`: Tells `uvx` to fetch the package from this Git repository.
    -   `pypreader-mcp`: The name of the console script to run (defined in `pyproject.toml`).
    -   `--python_path`: **Crucially**, you must provide the absolute path to the Python executable of the environment you want the AI to inspect. This could be your project's virtual environment.

### Server Parameters

When configuring the MCP server in your AI environment, you can specify the following command-line arguments:

-   `--python_path`: Specifies the path to the Python executable of the environment where your target packages are installed. If not provided, it defaults to the Python executable running the server. You can find the correct path by activating your project's Python environment and running `which python` in your terminal.
-   `--logging_level`: Sets the logging level for the server. Options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default is `INFO`.

**Example Configuration with Parameters:**

```json
{
    "name": "pypreader-mcp",
    "command": [
        "python",
        "-m",
        "pypreader_mcp.server",
        "--python_path",
        "/path/to/your/project/venv/bin/python",
        "--logging_level",
        "DEBUG"
    ],
    "mac_command": [],
    "linux_command": [],
    "windows_command": [],
    "env": {},
    "working_directory": "/path/to/pypreader-mcp"
}
```

### Testing with a Client

If you want to test the server or understand its capabilities, you can use a client like `fastmcp`. The code in `examples/fastmcp_client.py` demonstrates how to connect to and call the server's tools.

```python:examples/fastmcp_client.py
import sys
import asyncio
from fastmcp import Client
from fastmcp.client.transports import UvxStdioTransport


# This transport assumes the server is installed from a git repository
# and can be run via `uvx`.
transport = UvxStdioTransport(
    from_package="git+https://github.com/zakahan/pypreader-mcp.git",
    tool_name="pypreader-mcp",
    env_vars={
        "python_path": sys.executable, # Tell the server to inspect the current python env
        "logging_level": "ERROR",
    },
)


async def main():
    async with Client(transport) as client:
        print("> 1. Listing available tools...")
        tools = await client.list_tools()
        for tool in tools:
            print(f"- {tool.name}")

        print("\n> 2. Getting directory for 'fastmcp' package...")
        result = await client.call_tool(
            name="get_package_directory", arguments={"package_name": "fastmcp"}
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())

```

## Development

1.  **Setup**: Clone the repository and create a virtual environment.

    ```bash
    git clone https://github.com/your-username/pypreader-mcp.git
    cd pypreader-mcp
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install Dependencies**: Install the package in editable mode with development dependencies.

    ```bash
    pip install -e ".[dev]"
    ```

3.  **Code Quality**: This project uses `ruff` for linting and formatting, managed via `pre-commit`.

    ```bash
    # Install pre-commit hooks
    pre-commit install

    # Run against all files
    pre-commit run --all-files
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.