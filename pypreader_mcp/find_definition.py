import argparse
import inspect
import importlib
import ast


def find_definition_with_range(package_name: str, symbol_name: str) -> dict:
    """
    Find the definition location and code range of symbols in Python package

    Returns:
        {
            'name': Symbol name,
            'type': Symbol type,
            'file': File path,
           'start_line': Starting line,
            'end_line': Ending line,
            'code': Source code
        }
    """
    try:
        # Import package and get symbol objects
        module = importlib.import_module(package_name)
        obj = module
        for part in symbol_name.split("."):
            obj = getattr(obj, part)

        # Get the source file and the starting line
        source_file = inspect.getsourcefile(obj)
        source_lines, start_line = inspect.getsourcelines(obj)

        # Parse the AST to get the end line
        with open(source_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        # Locate the target node
        target_node = None
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ClassDef)
                and node.name == symbol_name.split(".")[-1]
            ) or (
                isinstance(node, ast.FunctionDef)
                and node.name == symbol_name.split(".")[-1]
            ):
                target_node = node
                break

        if target_node:
            end_line = target_node.end_lineno  # # Python 3.8+ supports end_lineno
            code = "".join(source_lines)
        else:
            # Fallback solution: Estimate the end line using the starting line and the number of code lines
            end_line = start_line + len(source_lines) - 1
            code = "".join(source_lines)

        return {
            "name": symbol_name,
            "type": "class" if inspect.isclass(obj) else "function",
            "file": source_file,
            "start_line": start_line,
            "end_line": end_line,
            "code": code,
        }

    except Exception as e:
        return {
            "code": f"Error: failed to locate {symbol_name} in {package_name}: {str(e)}"
        }


if __name__ == "__main__":
    args_parse = argparse.ArgumentParser()
    args_parse.add_argument(
        "--package_name",
        type=str,
        required=True,
        help="The name of the package, such as `requests`",
    )

    args_parse.add_argument(
        "--symbol_name",
        type=str,
        required=True,
        help="The name of the symbol, it can be function_name or class_name, such as `get` or `Session`",
    )

    args = args_parse.parse_args()

    result = find_definition_with_range(args.package_name, args.symbol_name)
    print(result["code"])
