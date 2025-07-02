import os.path

from fastmcp import FastMCP

from pypreader_mcp.utils import get_package_path, list_directory_contents

mcp = FastMCP(
    "Python Package Reader MCP Server 🥳",
)


@mcp.tool
def get_package_directory(package_name: str) -> str:
    """
    Get the directory of the specified package.
    Args:
        package_name: The name of the package, such as `mcp`.
    Returns:
        str: The directory of the package.
    """
    try:
        package_path = get_package_path(package_name)
        package_content = list_directory_contents(package_path)
    except ImportError:
        return f"Package `{package_name}` is not installed. Please install it first."
    return "\n".join(package_content)


@mcp.tool
def get_source_code(file_path: str):
    """
    Get the source code of the specified file to obtain more detailed and specific information.
    Args:
        file_path: The file path, which is a path similar to `mcp/server/models.py` that you query in the `get_package_directory` tool.
    Returns:
        str: The source code of the file.
    """
    try:
        site_package_path = os.path.dirname(
            get_package_path("mcp")
        )  # This must be in the dependencies.
    except ImportError:
        return "Package `mcp` is not installed. Please install it first."

    path = os.path.join(site_package_path, file_path)
    if not os.path.exists(path):
        return f"File `{file_path}` does not exist."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
