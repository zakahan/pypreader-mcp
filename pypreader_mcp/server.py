import os
import sys
import re
import logging
import subprocess
import requests
from fastmcp import FastMCP

from pypreader_mcp.utils import get_package_path, list_directory_contents

CURRENT_PYTHON_PATH = os.getenv("CURRENT_PYTHON_PATH", sys.executable)
LOGGING_LEVEL = os.getenv("CURRENT_LOGGING_LEVEL", "INFO")

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_LEVEL),
    format="pypreader-mcp: %(levelname)s - %(message)s",
)

# Check if the default value is used
if CURRENT_PYTHON_PATH == sys.executable:
    logging.info(f"Using default Python path: {CURRENT_PYTHON_PATH}")


def check_python_path() -> str:
    """
    Check if the Python environment is valid.
    """
    if not os.path.exists(CURRENT_PYTHON_PATH):
        raise ValueError(
            f"Python environment not found: {CURRENT_PYTHON_PATH}. Please check the path."
        )

    # Check if the file is executable
    if not os.access(CURRENT_PYTHON_PATH, os.X_OK):
        raise PermissionError(
            f"The file {CURRENT_PYTHON_PATH} is not executable. Please check the file permissions."
        )

    try:
        result = subprocess.run(
            [CURRENT_PYTHON_PATH, "-V"],
            capture_output=True,
            text=True,
            check=True,
        )
        # Check both standard output and standard error output simultaneously
        output = result.stdout.strip() or result.stderr.strip()
        if not re.match(r"Python \d+\.\d+\.\d+", output):
            raise ValueError(
                f"The file {CURRENT_PYTHON_PATH} does not appear to be a valid Python executable."
            )
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f"Failed to execute {CURRENT_PYTHON_PATH} as a Python executable: {e}"
        )

    return CURRENT_PYTHON_PATH


def get_site_packages_path(python_path: str) -> str:
    site_packages_path = subprocess.run(
        [python_path, "-c", "import site; print(site.getsitepackages()[0])"],
        capture_output=True,
        text=True,
        check=True,
    )
    return site_packages_path.stdout.strip()


check_python_path()

PYTHON_PATH = CURRENT_PYTHON_PATH  # target python path
SITE_PACKAGE_PATH = get_site_packages_path(PYTHON_PATH)  # target site-packages path

PYP_READER_MCP_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

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
    except Exception as e:
        return f"Package `{package_name}` is not installed. Please install it first. Error detail: {e.__class__.__name__}: {e}"
    return "\n".join(package_content)


@mcp.tool
def get_source_code_by_path(package_path: str) -> str:
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


@mcp.tool
def get_source_code_by_symbol(package_name: str, symbol_name: str) -> str:
    """
    Obtain the source code of a specified symbol in a specified package,
    The symbol can be a function or a class.
    Compared with `get_source_code_by_path`, this tool can locate the specified symbol code segment more accurately.
    Args:
        package_name: The name of the package, such as `requests`.
        symbol_name: The name of the symbol, it could be a function or a class, such as `get` or `Session`.
    Returns:
        str: The definition of the symbol a string of code.
    """
    symbol_name = symbol_name.strip()
    code = subprocess.run(
        [
            PYTHON_PATH,
            os.path.join(PYP_READER_MCP_DIR_PATH, "find_symbol.py"),
            "--package_name",
            package_name,
            "--symbol_name",
            symbol_name,
            "--logging_level",
            LOGGING_LEVEL,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return code.stdout.strip()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
