"""
backend/safety.py

Backend Safety Screening module for the Req2Py hackathon project.

This module performs BASIC STATIC safety screening of AI-generated
Python code using only the built-in `ast` module. It looks for
dangerous imports, dangerous function calls, and dangerous
attribute/method usage (e.g. os.system).

It does NOT:
    - Execute the generated code in any way.
    - Use eval() or exec() to analyze the code.
    - Implement the Flask API.
    - Implement pipeline.py.

Other modules (e.g. pipeline.py) should import and call `check_safety()`
as the single entry point for safety screening of generated code.
"""

import ast
from typing import Any, Dict, List


# Modules that are considered potentially dangerous to import.
DANGEROUS_IMPORTS = {
    "subprocess",
    "os",
    "sys",
    "ctypes",
    "pickle",
    "marshal",
}

# Function names that are considered dangerous to call directly.
DANGEROUS_CALLS = {
    "eval",
    "exec",
    "compile",
    "__import__",
}

# Dangerous attribute/method usage, expressed as (object_name, attribute_name).
# e.g. os.system(...), os.popen(...), os.remove(...), etc.
DANGEROUS_ATTRIBUTES = {
    ("os", "system"),
    ("os", "popen"),
    ("os", "remove"),
    ("os", "unlink"),
    ("os", "rmdir"),
}


def _make_issue(issue_type: str, message: str) -> Dict[str, str]:
    """Build a single issue dictionary in a consistent shape."""
    return {"type": issue_type, "message": message}


def check_safety(code: str) -> Dict[str, Any]:
    """
    Perform basic static safety screening of Python source code.

    This function never executes the given code. It parses the code
    into an Abstract Syntax Tree (AST) using `ast.parse()` and walks
    the tree looking for:
        - Dangerous imports (e.g. subprocess, os, sys, ctypes, pickle,
          marshal).
        - Dangerous function calls (e.g. eval, exec, compile,
          __import__).
        - Dangerous attribute/method usage (e.g. os.system, os.popen,
          os.remove, os.unlink, os.rmdir).

    Args:
        code: The Python source code to screen, as a string.

    Returns:
        A dictionary with the following keys:
            - safe (bool): True if no issues were found.
            - issues (list[dict]): A list of issue dictionaries, each
              with a "type" and a "message" key. Empty if the code is
              safe.
    """
    issues: List[Dict[str, str]] = []

    if not isinstance(code, str):
        return {
            "safe": False,
            "issues": [
                _make_issue(
                    "invalid_input",
                    "Input code must be a string.",
                )
            ],
        }

    # Step 1: Parse the code. Never execute it.
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "safe": False,
            "issues": [
                _make_issue(
                    "syntax_error",
                    f"Code could not be parsed: {exc.msg} "
                    f"(line {exc.lineno}, column {exc.offset}).",
                )
            ],
        }
    except (ValueError, TypeError) as exc:
        return {
            "safe": False,
            "issues": [
                _make_issue(
                    "parse_error",
                    f"Code could not be parsed: {exc}",
                )
            ],
        }

    # Step 2: Walk the AST and look for dangerous patterns.
    for node in ast.walk(tree):

        # --- Dangerous imports: `import os`, `import subprocess as sp` ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.split(".")[0]
                if module_name in DANGEROUS_IMPORTS:
                    issues.append(
                        _make_issue(
                            "dangerous_import",
                            f"Potentially dangerous import detected: '{alias.name}' "
                            f"(line {node.lineno}).",
                        )
                    )

        # --- Dangerous imports: `from os import system` ---
        elif isinstance(node, ast.ImportFrom):
            module_name = (node.module or "").split(".")[0]
            if module_name in DANGEROUS_IMPORTS:
                issues.append(
                    _make_issue(
                        "dangerous_import",
                        f"Potentially dangerous import detected: 'from {node.module} "
                        f"import ...' (line {node.lineno}).",
                    )
                )

        # --- Dangerous function calls and dangerous attribute calls ---
        elif isinstance(node, ast.Call):
            func = node.func

            # Direct calls like eval(...), exec(...), compile(...), __import__(...)
            if isinstance(func, ast.Name) and func.id in DANGEROUS_CALLS:
                issues.append(
                    _make_issue(
                        "dangerous_call",
                        f"Potentially dangerous function call detected: "
                        f"'{func.id}()' (line {node.lineno}).",
                    )
                )

            # Attribute calls like os.system(...), os.popen(...), etc.
            elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                pair = (func.value.id, func.attr)
                if pair in DANGEROUS_ATTRIBUTES:
                    issues.append(
                        _make_issue(
                            "dangerous_attribute",
                            f"Potentially dangerous call detected: "
                            f"'{pair[0]}.{pair[1]}()' (line {node.lineno}).",
                        )
                    )

    return {
        "safe": len(issues) == 0,
        "issues": issues,
    }


if __name__ == "__main__":
    # Simple demonstration of check_safety(). This block only analyzes
    # strings with `ast` - it never executes any of the sample code below.

    print("=== 1. Safe code ===")
    safe_sample = "x = 1\ny = 2\nprint(x + y)\n"
    print(check_safety(safe_sample))

    print("\n=== 2. Code containing eval() ===")
    eval_sample = "user_input = '1 + 1'\nresult = eval(user_input)\n"
    print(check_safety(eval_sample))

    print("\n=== 3. Code containing subprocess ===")
    subprocess_sample = "import subprocess\nsubprocess.run(['ls'])\n"
    print(check_safety(subprocess_sample))

    print("\n=== 4. Code containing os.system() ===")
    os_system_sample = "import os\nos.system('rm -rf /')\n"
    print(check_safety(os_system_sample))
