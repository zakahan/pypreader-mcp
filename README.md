# pypreader-mcp

[English](./README.md) | [简体中文](./README_zh.md)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package reading Server that implements the Model Context Protocol (MCP). This Server allows large language models (LLMs) and other AI agents to inspect the contents of Python packages in a specified environment.

## Overview

`pypreader-mcp` acts as a bridge between AI models and the local Python environment. By exposing a set of tools through the Model Context Protocol, it enables AI to programmatically browse installed packages, view their file structures, and read their source code. This is useful for tasks such as code analysis, dependency checking, and automated programming assistance.

### Why was this created?

When I used AI-integrated programming IDEs like Cursor or Trae, I always found that the currently used models didn't know about the third-party libraries I needed. Sometimes they would seriously generate a bunch of indescribable stuff, and sometimes they would search the internet, but basically, the results were not good, and it was hard to find any useful information.

So I created this MCP service. It can read documentation from the official website pypi.org or read the source code from the site-packages environment corresponding to your Python, to more directly understand the content of the third-party libraries you want to use.

## Features

The Server provides the following tools to MCP clients:

- `get_pypi_description(package_name: str)`: Retrieve the official description of a package from PyPI.
- `get_package_directory(package_name: str)`: List the entire file and directory structure of a specified installed package.
- `get_source_code_by_path(package_path: str)`: Retrieve the complete source code of a specific file within a package.
- `get_source_code_by_symbol(package_path: str, symbol_name: str)`: Obtain the definition (code snippet) of a specified symbol (function, class, etc.).

## Usage

This tool is designed to act as an MCP Server for use in AI-based environments such as [Cursor](https://cursor.sh/) or [Trae](https://trae.ai/). It is not intended to be directly cloned and run manually.

### Configuration

In the MCP Server configuration of your AI environment, add a new Server with the following settings. This allows the AI to run the service directly from its Git repository using `uvx`.

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

- **`command`**: `uvx`, a tool used to run Python applications from various sources.
- **`args`**:
    - `--from git+https://github.com/zakahan/pypreader-mcp.git`: Tells `uvx` to fetch the package from this Git repository.
    - `pypreader-mcp`: The name of the console script to run (defined in `pyproject.toml`).
    - `--python_path`: **Crucially**, you must provide the absolute path to the Python executable of the environment you want the AI to inspect. This might be your project's virtual environment.

### MCP-Server Parameters

When configuring the MCP Server in your AI environment, you can specify the following command-line parameters:

- `--python_path`: Specifies the path to the Python executable of the target package installation environment. If not provided, it defaults to the Python executable running the Server. You can find the correct path by activating your project's Python environment and running `which python` in the terminal.
- `--logging_level`: Sets the logging level of the Server. Options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default is `INFO`.

If you use a Python virtual environment to configure your Python project, you typically need to modify `python_path` at any time to switch to your specified Python environment.

### AI Coding Example

Take Trae as an example. Currently (2025-07-02), the doubao-seed-1.6 model does not know the `fastmcp` package (in fact, most models don't either). Under normal circumstances, it would either pretend to know and output a bunch of messy, indescribable error content, even thinking I was talking about FastAPI, or it would perform a stiff search and find all kinds of disorganized information.

This time, I created a Trae agent equipped with this project's mcp-server. The result is as follows: Trae can understand my project and then write `fastmcp` services to complete my task.

**This is the entire process of Trae completing my requested task**

![trae_examples](./assets/images/trae_example.png)

**These are the specific details of the tool calls**

![tools](./assets/images/tools_call_response.png)


### Testing with a Client

If you want to test this service or understand its functionality, you can use a client like `fastmcp`. The code in `examples/fastmcp_client.py` demonstrates how to connect to the Server and call its tools.

## Development

1.  **Setup**: Clone the repository and create a virtual environment.

    ```bash
    git clone https://github.com/your-username/pypreader-mcp.git
    cd pypreader-mcp
    uv venv --python 3.10
    source .venv/bin/activate
    ```

2.  **Install Dependencies**: Install the package and its development dependencies in editable mode.

    ```bash
    pip install -e ".[dev]"
    ```

3.  **Code Quality**: This project uses `ruff` for code checking and formatting, managed via `pre-commit`.

    ```bash
    # Install pre-commit hooks
    pre-commit install

    # Run on all files
    pre-commit run --all-files
    ```

## License

This project is licensed under the MIT License. For details, see the [LICENSE](LICENSE) file.

### What's New Now?

- 2025-07-04: Rewrote the `get_source_code_by_symbol` tool, fixing the issue where classes or functions belonging to sub-packages could not be read.


### What's Next?

1. Resolve the issue where `python-package-name` is inconsistent with the actual path, e.g., the package name `google-adk` has an actual path `google.adk`
2. Design a suitable prompt for the Agent.