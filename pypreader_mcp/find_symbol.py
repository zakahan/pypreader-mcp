import os
import logging
import argparse
import inspect
import importlib
from typing import Any

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "--package_name",
    type=str,
    required=True,
    help="The name of the package, such as `requests`",
)

arg_parser.add_argument(
    "--symbol_name",
    type=str,
    required=True,
    help="The name of the symbol, it can be function_name or class_name, such as `get` or `Session`",
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
    format="pypreader-mcp - find_symbol: %(levelname)s - %(message)s",
)


def get_py_files(root_dir, package_name):
    py_modules = []
    package_root = os.path.abspath(root_dir)
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.abspath(str(os.path.join(root, file)))
                # 获取相对路径
                relative_path = os.path.relpath(file_path, package_root)
                # 处理 __init__.py 的特殊情况
                if file == "__init__.py":
                    # 获取当前目录的模块名
                    module_name = os.path.relpath(root, package_root).replace(
                        os.sep, "."
                    )
                    # 如果是根目录的 __init__.py，直接用包名
                    if not module_name:
                        module_name = os.path.basename(package_root)
                else:
                    # 去掉 .py 扩展名
                    relative_path = relative_path[:-3]
                    # 替换路径分隔符为点号
                    module_name = relative_path.replace(os.sep, ".")
                py_modules.append(module_name)

    real_py_modules = []
    for modules_str in py_modules:
        if modules_str == ".":
            continue
        else:
            real_py_modules.append(f"{package_name}.{modules_str}")
    return real_py_modules


# init
def find_from_init(package_name: str, symbol_name: str):
    module = importlib.import_module(package_name)
    obj = module
    for part in symbol_name.split("."):
        obj = getattr(obj, part)
    return obj


#
def find_from_sub_packages(package_name: str, symbol_name: str) -> Any:
    module = importlib.import_module(package_name)
    module_path = module.__file__ if hasattr(module, "__file__") else None
    if module_path is None:
        raise ImportError(f"Module {package_name} has no __file__ attribute")
    all_py_list = get_py_files(os.path.dirname(module_path), package_name)
    for module_str in all_py_list:
        sub_module = importlib.import_module(module_str)
        obj = getattr(sub_module, symbol_name, None)
        if obj is not None:
            return obj
    return None


def find_definition_with_range(package_name: str, symbol_name: str) -> str:
    """
    Find the definition location and code range of symbols in Python package

    Returns:
        dict: A dictionary containing the symbol name, type, file path, starting line, and code.
              If the symbol is not found, an error message will be returned.
    """
    try:
        # Step 1 Import package by __init__
        try:
            obj = find_from_init(package_name, symbol_name)
        except ImportError as e:
            return f"Package `{package_name}` is not installed. Please install it first. Detail error: {str(e)}"
        except Exception:
            logging.info(
                f"can't find `{symbol_name}` in `{package_name}`.__init__.py, expand the search scope to the entire package."
            )
            # Step 2: Import package by the same level of __init__.py
            obj = find_from_sub_packages(package_name, symbol_name)
            if obj is None:
                return f"can't find `{symbol_name}` in `{package_name}` and it's sub-modules, maybe `{symbol_name}` is in other package or it doesn't exist."

        # Get the source file and the starting line

        source_lines, start_line = inspect.getsourcelines(obj)  # list[str], int
        # source_file = inspect.getsourcefile(obj)
        # symbol_type = "class" if inspect.isclass(obj) else "function"
        # end_line = start_line + len(source_lines) - 1
        source_code = "".join(source_lines)
        obj_module_name = obj.__module__
        if obj_module_name != package_name:
            return (
                source_code
                + f"\n# Extra Message: this symbol is not in `{package_name}`, the actual module is `{obj_module_name}`\n"
            )
        return source_code

    except Exception as e:
        return f"An error occurred while finding the definition: {e.__class__}:{str(e)}"


def find_symbol(package_name: str, symbol_name: str) -> str:
    return find_definition_with_range(package_name, symbol_name)


if __name__ == "__main__":
    result = find_symbol(args.package_name, args.symbol_name)
    print(result)
