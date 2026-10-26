"""
tests/test_requirement_processor.py
Unit tests for input requirement validation and sanitization.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend


class TestRequirementProcessor(unittest.TestCase):
    """Test suite for requirement processor input validation."""

    def test_empty_requirement_rejected(self):
        """Verify empty requirement strings raise a ValueError."""
        with self.assertRaises(ValueError):
            backend.generate("")

    def test_whitespace_only_requirement_rejected(self):
        """Verify whitespace-only requirements raise a ValueError."""
        with self.assertRaises(ValueError):
            backend.generate("   \n\t  ")

    def test_none_requirement_rejected(self):
        """Verify None raises a ValueError."""
        with self.assertRaises(ValueError):
            backend.generate(None)  # type: ignore

    def test_valid_requirement_accepted(self):
        """Verify a valid natural-language requirement is accepted and processed."""
        result = backend.generate(
            requirement="Create a Python function that checks whether a number is prime and returns True or False.",
            constraints="Must be O(sqrt(n))",
            language="Python",
        )
        self.assertIsInstance(result, dict)
        self.assertIn("generated_code", result)
        self.assertIn("validation", result)
        self.assertEqual(result["validation"]["status"], "Passed")

    def test_age_conditional_synthesis(self):
        """Verify exact conditional requirement creates accurate if-else code."""
        result = backend.generate("Create a Python code for if age>=18 print adult ,else teen")
        self.assertEqual(result["validation"]["status"], "Passed")
        self.assertIn("def check_age", result["generated_code"])
        self.assertIn("if age >= 18:", result["generated_code"])
        self.assertIn('print("adult")', result["generated_code"])
        self.assertIn('print("teen")', result["generated_code"])


def test_empty_requirement_rejected():
    """Pytest-compatible wrapper."""
    case = TestRequirementProcessor()
    case.test_empty_requirement_rejected()


def test_valid_requirement_accepted():
    """Pytest-compatible wrapper."""
    case = TestRequirementProcessor()
    case.test_valid_requirement_accepted()


if __name__ == "__main__":
    unittest.main()
