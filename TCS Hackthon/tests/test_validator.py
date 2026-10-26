"""
tests/test_validator.py
Unit tests for backend AST syntax and structural validation.
Compatible with both unittest and pytest.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.validator import validate_code, validate_structure, validate_syntax


class TestValidator(unittest.TestCase):
    """Test suite for Python AST syntax and structural validator."""

    def test_valid_python_syntax(self):
        """Verify valid Python snippets pass syntax validation."""
        valid_code = "def is_even(n: int) -> bool:\n    return n % 2 == 0\n"
        result = validate_syntax(valid_code)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["error_type"])
        self.assertIsNone(result["error_message"])

    def test_invalid_python_syntax(self):
        """Verify syntax errors are caught with line and column information."""
        invalid_code = "def broken(x\n    return x + 1\n"
        result = validate_syntax(invalid_code)
        self.assertFalse(result["valid"])
        self.assertEqual(result["error_type"], "SyntaxError")
        self.assertIsNotNone(result["line"])
        self.assertIsNotNone(result["error_message"])

    def test_non_string_input_rejected(self):
        """Verify non-string inputs are rejected gracefully."""
        result = validate_syntax(12345)  # type: ignore
        self.assertFalse(result["valid"])
        self.assertEqual(result["error_type"], "TypeError")

    def test_structural_analysis_counts(self):
        """Verify AST node counts for functions, classes, imports, loops, and conditionals."""
        code = '''import math
import sys
from typing import List

class Calculator:
    def __init__(self):
        self.history = []

    def compute(self, items: List[int]) -> int:
        total = 0
        for item in items:
            if item > 0:
                total += item
        return total
'''
        result = validate_structure(code)
        self.assertTrue(result["valid"])
        self.assertEqual(result["classes"], 1)
        self.assertEqual(result["functions"], 2)  # __init__ and compute
        self.assertEqual(result["imports"], 3)
        self.assertEqual(result["loops"], 1)
        self.assertEqual(result["conditionals"], 1)

    def test_validate_code_combined(self):
        """Verify validate_code combines syntax and structure properly."""
        code = "def add(a, b):\n    return a + b\n"
        res = validate_code(code)
        self.assertTrue(res["valid"])
        self.assertTrue(res["syntax"]["valid"])
        self.assertIsNotNone(res["structure"])
        self.assertEqual(res["structure"]["functions"], 1)


def test_valid_python_placeholder():
    """Pytest-compatible function runner."""
    case = TestValidator()
    case.test_valid_python_syntax()


def test_invalid_python_placeholder():
    """Pytest-compatible function runner."""
    case = TestValidator()
    case.test_invalid_python_syntax()


if __name__ == "__main__":
    unittest.main()
