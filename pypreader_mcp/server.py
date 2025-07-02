import re
import sys
import argparse
import os.path
import subprocess
import logging

import requests
from fastmcp import FastMCP
from pypreader_mcp.utils import get_package_path, list_directory_contents

arg_parser = argparse.ArgumentParser(description="MCP Server")
arg_parser.add_argument(
    "--python_path",
    type=str,
    default=sys.executable,
    help="The path of the Python environment where your target project is located. You can view and obtain it by entering `which python` in the project path (when the Python environment is activated).",
)
arg_parser.add_argument(
    "--logging_level",
    type=str,
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Logging level for the server.",
)

args = arg_parser.parse_args()


# Configure logging
logging.basicConfig(
    level=getattr(logging, args.logging_level),
    format="pypreader-mcp: %(levelname)s - %(message)s",
)


# Check if the default value is used
if args.python_path == sys.executable:
    logging.info(f"Using default Python path: {args.python_path}")


def check_python_path() -> str:
    """
    Check if the Python environment is valid.
    """
    if not os.path.exists(args.python_path):
        raise ValueError(
            f"Python environment not found: {args.python_path}. Please check the path."
        )

    # Check if the file is executable
    if not os.access(args.python_path, os.X_OK):
        raise PermissionError(
            f"The file {args.python_path} is not executable. Please check the file permissions."
        )

    try:
        result = subprocess.run(
            [args.python_path, "-V"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Check both standard output and standard error output simultaneously
        output = result.stdout.strip() or result.stderr.strip()
        if not re.match(r"Python \d+\.\d+\.\d+", output):
            raise ValueError(
                f"The file {args.python_path} does not appear to be a valid Python executable."
            )
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"Failed to execute {args.python_path} as a Python executable: {e}"
        )

    return args.python_path


def get_site_packages_path(python_path_path: str) -> str:
    site_packages_path = subprocess.run(
        [python_path_path, "-c", "import site; print(site.getsitepackages()[0])"],
        capture_output=True,
        text=True,
        check=True,
    )
    return site_packages_path.stdout.strip()


check_python_path()
SITE_PACKAGE_PATH = get_site_packages_path(args.python_path)


mcp = FastMCP(
    "Python Package Reader MCP Server 🥳",
)


@mcp.tool
def get_pypi_description(package_name: str) -> str:
    """
    Get the description of the specified package on PyPI.
    Args:
        package_name: The name of the package, such as `requests`.
    Returns:
        str: The description of the package.
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Handle errors such as 404
        data = response.json()
        return data["info"]["description"]  # Return package description
    except requests.exceptions.RequestException as e:
        return f"Failed to obtain:{e}"


@mcp.tool
def get_package_directory(package_name: str) -> str:
    """
    Get the directory of the specified package.
    Args:
        package_name: The name of the package, such as `requests`.
    Returns:
        str: The directory of the package.
    """
    try:
        package_path = get_package_path(package_name, SITE_PACKAGE_PATH)
        package_content = list_directory_contents(package_path)
    except ImportError:
        return f"Package `{package_name}` is not installed. Please install it first."
    return "\n".join(package_content)


@mcp.tool
def get_source_code(package_path: str):
    """
    Get the source code of the specified file to obtain more detailed and specific information.
    Args:
        package_path: The package path, which is a path similar to `requests/api.py` that you query in the `get_package_directory` tool.
    Returns:
        str: The source code of the file.
    """
    path = os.path.join(SITE_PACKAGE_PATH, package_path)
    if not os.path.exists(path):
        return f"File `{package_path}` does not exist."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
