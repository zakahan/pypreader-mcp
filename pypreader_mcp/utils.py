import os.path
import importlib.util


def get_package_path(package_name: str):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise ImportError(f"Package {package_name} not found.")
    if spec.origin == "built-in":  # Handle built - in modules (such as sys, os)
        raise ImportError(
            f"Package {package_name} is a built-in module and cannot be imported."
        )
    path = os.path.dirname(spec.origin)
    return path


# Define the directory names to be filtered
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "egg-info",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
}

# Define the file extensions to be filtered
IGNORE_EXTS = {".pyc", ".pyo", ".pyd", ".so", ".dll", ".egg-info", ".DS_Store"}


def should_ignore(path, is_dir=False):
    """Determine whether this path should be ignored"""
    if is_dir:
        return os.path.basename(path) in IGNORE_DIRS
    else:
        return os.path.splitext(path)[1] in IGNORE_EXTS


def list_directory_contents(directory):
    """Recursively list all contents in a directory and return a list instead of printing."""
    result = []  # The list to store the results

    try:
        # Get the base name of the directory, which is used to construct the relative path
        base_dir = os.path.basename(os.path.abspath(directory))

        # Traverse the directory tree
        for root, dirs, files in os.walk(directory):
            # Calculate the path of the current sub-directory relative to the input directory
            relative_path = os.path.relpath(root, directory)

            # If it is the root directory, relative_path will be '.', and special handling is required.
            if relative_path == ".":
                current_dir = base_dir
            else:
                current_dir = os.path.join(base_dir, relative_path)

            # Filter out unwanted directories (modify dirs before traversing)
            dirs[:] = [d for d in dirs if not should_ignore(d, is_dir=True)]

            # Add subdirectories to the result list
            result.append(f"{current_dir}/")

            # Add files in subdirectories to the result list (filter out unwanted files)
            for file in files:
                if not should_ignore(file):
                    result.append(f"{os.path.join(current_dir, file)}")

    except NotADirectoryError:
        return f"Error: '{directory}' is not a valid directory."
    except PermissionError:
        return f"Error: No permission to access directory '{directory}'."
    except FileNotFoundError:
        return f"Error: Directory '{directory}' does not exist."
    except Exception as e:
        return f"An unknown error occurred: {e}"
    return result  # Return the result list


if __name__ == "__main__":
    x = get_package_path("requests")
    y = list_directory_contents(x)
    print(y)
