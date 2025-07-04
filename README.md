# pypreader-mcp

[English](./README.md) | [简体中文](./README_zh.md)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python Package Reader server implementing the Model Context Protocol (MCP). This server allows Large Language Models (LLMs) and other AI agents to inspect the contents of Python packages within a specified environment.

## Overview

`pypreader-mcp` acts as a bridge between an AI model and a local Python environment. By exposing a set of tools through the Model Context Protocol, it enables the AI to programmatically browse installed packages, view their file structure, and read their source code. This is useful for tasks like code analysis, dependency inspection, and automated programming assistance.

### Why do this?

When I use AI-integrated programming IDEs such as Cursor or Trae, I always find that the currently used model is not aware of the third - party libraries I need. Sometimes, when they search the Internet, it's always a mess and it's difficult to find any useful information. 

So I made this MCP server. It can read the documentation from the official website pypi.org or read the source code in your Python's site - packages environment, in order to more directly understand the content of the third - party library you want to use.

## Features

The server provides the following tools to an MCP client:

- `get_pypi_description(package_name: str)`: Fetches the official description of a package from PyPI.
- `get_package_directory(package_name: str)`: Lists the entire file and directory structure of a specified installed package.
- `get_source_code_by_path(package_path: str)`: Retrieve the complete source code of a specific file within the package.
- `get_source_code_by_symbol(package_path: str, symbol_name: str)`: Obtain the definition (code segment) of the specified symbol (function, class, etc.).

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

- **`command`**: Should be `uvx`, which is a tool for running Python applications from various sources.
- **`args`**: 
  - `--from git+https://github.com/zakahan/pypreader-mcp.git`: Tells `uvx` to fetch the package from this Git repository.
  - `pypreader-mcp`: The name of the console script to run (defined in `pyproject.toml`).
  - `--python_path`: **Crucially**, you must provide the absolute path to the Python executable of the environment you want the AI to inspect. This could be your project's virtual environment.

### Server Parameters

When configuring the MCP server in your AI environment, you can specify the following command-line arguments:

- `--python_path`: Specifies the path to the Python executable of the environment where your target packages are installed. If not provided, it defaults to the Python executable running the server. You can find the correct path by activating your project's Python environment and running `which python` in your terminal.
- `--logging_level`: Sets the logging level for the server. Options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default is `INFO`.

If you use a Python virtual environment to configure a Python project, generally, you need to modify the python_path at any time to switch to the Python environment you specified.

### AI-Coding Example

Take Trae as an example. Currently (2025-07-02), the doubao-seed-1.6 model doesn't know about the `fastmcp` package(In fact, most models don't recognize it either). In the normal process, it would either pretend to know and output a bunch of messy and indescribable hallucinations, or it would do a hard search and find all kinds of messy things. 

This time, I created a Trae Agent, which is equipped with the mcp-server of this project. As a result, Trae can understand my project and then write the service of fastmcp to complete my task. 

**This is the whole process of Trae completing the task I requested**

![trae_examples](./assets/images/trae_example.png)

**These are the specific details of the tool call**

![tools](./assets/images/tools_call_response.png)


### Testing with a Client

If you want to test the server or understand its capabilities, you can use a client like `fastmcp`. The code in `examples/fastmcp_client.py` demonstrates how to connect to and call the server's tools.

## Development

1.  **Setup**: Clone the repository and create a virtual environment.

    ```bash
    git clone https://github.com/your-username/pypreader-mcp.git
    cd pypreader-mcp
    uv venv --python 3.10
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

### What's New Now?

- 2025-07-04: Rewrote the `get_source_code_by_symbol` tool, fixing the issue of not being able to read classes or functions belonging to sub-packages.