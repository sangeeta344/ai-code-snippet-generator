"""
backend/pipeline.py
 
Backend Validation Pipeline module for the Req2Py hackathon project.
 
This module combines the existing validator.py and safety.py modules
into ONE end-to-end validation pipeline for AI-generated Python code:
 
    1. Syntax validation   (validator.validate_syntax)
    2. Structural analysis (validator.validate_structure)
    3. Safety screening    (safety.check_safety)
 
It does NOT:
    - Execute the generated code in any way.
    - Use eval() or exec().
    - Implement the Flask API.
    - Call Ollama or any LLM.
    - Implement auto-correction.
 
This module is intended to be the single entry point that other parts
of the project (e.g. a future Flask API) call to fully validate a piece
of AI-generated Python code.
"""
 
from typing import Any, Dict, List
 
try:
    from backend.validator import validate_syntax, validate_structure
    from backend.safety import check_safety
except (ImportError, ModuleNotFoundError):
    from validator import validate_syntax, validate_structure
    from safety import check_safety
 
 
def validate_code_pipeline(code: str) -> Dict[str, Any]:
    """
    Run the full backend validation pipeline on a piece of Python code.
 
    Steps:
        1. Run syntax validation.
        2. If syntax is invalid, skip structural validation (it would
           be meaningless), still run a safety check for visibility,
           and return a FAILED result describing the syntax error.
        3. If syntax is valid, run structural validation and safety
           screening.
        4. Combine everything into one final result dictionary.
 
    Overall status is "PASSED" only when all three of the following
    are true:
        - syntax is valid
        - structure is valid
        - safety check reports the code as safe
 
    Otherwise, status is "FAILED".
 
    Args:
        code: The Python source code to validate, as a string.
 
    Returns:
        A dictionary with the following keys:
            - status (str): "PASSED" or "FAILED".
            - valid (bool): True only if syntax, structure, and safety
              all check out.
            - syntax (dict): Result of validate_syntax(code).
            - structure (dict | None): Result of validate_structure(code),
              or None if syntax validation failed.
            - safety (dict | None): Result of check_safety(code), or
              None only if an unexpected internal error prevented the
              safety check from running.
            - errors (list[str]): Human-readable error messages.
            - warnings (list[str]): Human-readable, non-fatal warnings.
    """
    errors: List[str] = []
    warnings: List[str] = []
 
    try:
        # Step 1: Syntax validation.
        syntax_result = validate_syntax(code)
 
        if not syntax_result["valid"]:
            # Step 2: Syntax is invalid - structural validation is
            # skipped since it would be meaningless on broken code.
            # We still run the safety check for visibility, but a
            # failure there doesn't need to be logged twice.
            errors.append(
                f"SyntaxError: {syntax_result['error_message']} "
                f"(line {syntax_result['line']}, column {syntax_result['column']})"
            )
 
            safety_result = check_safety(code)
            if not safety_result["safe"]:
                for issue in safety_result["issues"]:
                    # Avoid duplicating the same syntax error message
                    # that check_safety() also reports when it can't parse.
                    if issue["type"] != "syntax_error":
                        errors.append(f"Unsafe operation detected: {issue['message']}")
 
            return {
                "status": "FAILED",
                "valid": False,
                "syntax": syntax_result,
                "structure": None,
                "safety": safety_result,
                "errors": errors,
                "warnings": warnings,
            }
 
        # Step 3: Syntax is valid - run structural validation and safety screening.
        structure_result = validate_structure(code)
        safety_result = check_safety(code)
 
        if not structure_result["valid"]:
            errors.append(
                "Structural validation failure: "
                + (structure_result.get("error_message") or "Unknown structural error.")
            )
 
        if not safety_result["safe"]:
            for issue in safety_result["issues"]:
                errors.append(f"Unsafe operation detected: {issue['message']}")
 
        if structure_result["valid"]:
            if structure_result["functions"] == 0 and structure_result["classes"] == 0:
                warnings.append("No functions or classes were defined in this code.")
 
        # Step 4: Combine all results.
        overall_valid = (
            syntax_result["valid"]
            and structure_result["valid"]
            and safety_result["safe"]
        )
 
        return {
            "status": "PASSED" if overall_valid else "FAILED",
            "valid": overall_valid,
            "syntax": syntax_result,
            "structure": structure_result,
            "safety": safety_result,
            "errors": errors,
            "warnings": warnings,
        }
 
    except Exception as exc:  # noqa: BLE001 - deliberately broad for a robust pipeline
        # Handle any unexpected error gracefully instead of crashing.
        return {
            "status": "FAILED",
            "valid": False,
            "syntax": None,
            "structure": None,
            "safety": None,
            "errors": [f"Unexpected pipeline error: {exc}"],
            "warnings": [],
        }
 
 
def _print_result(test_name: str, code: str) -> None:
    """Helper for the __main__ test section: run the pipeline and print results clearly."""
    print(f"--- {test_name} ---")
    print("Code:")
    print(code)
    result = validate_code_pipeline(code)
    print(f"Status: {result['status']}")
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print()
 
 
if __name__ == "__main__":
    # These test cases only analyze code via ast - none of the sample
    # code below is ever executed.
 
    test_1_code = (
        "def add(a, b):\n"
        "    return a + b\n\n"
        "print(add(10, 20))\n"
    )
    _print_result("TEST 1: Valid code (expected PASSED)", test_1_code)
 
    test_2_code = (
        "def add(a, b)\n"
        "    return a + b\n"
    )
    _print_result("TEST 2: Invalid syntax (expected FAILED)", test_2_code)
 
    test_3_code = (
        "import subprocess\n"
        "subprocess.run(['echo', 'hello'])\n"
    )
    _print_result("TEST 3: Potentially unsafe code (expected FAILED)", test_3_code)
 
    test_4_code = (
        "import math\n\n"
        "def calculate(x):\n"
        "    if x > 10:\n"
        "        return math.sqrt(x)\n"
        "    return x\n"
    )
    _print_result("TEST 4: Function with import (expected PASSED)", test_4_code)