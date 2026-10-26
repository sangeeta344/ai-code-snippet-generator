"""
tests/test_safety_checker.py
Unit tests for backend AST static safety screening.
Ensures dangerous operations (eval, exec, os.system, subprocess) are flagged.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.safety import check_safety


class TestSafetyChecker(unittest.TestCase):
    """Test suite for AST-based safety screening."""

    def test_safe_code(self):
        """Verify standard math and string manipulation code is marked safe."""
        safe_code = '''import math

def calculate_circle_area(radius: float) -> float:
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    return math.pi * radius ** 2
'''
        result = check_safety(safe_code)
        self.assertTrue(result["safe"])
        self.assertEqual(len(result["issues"]), 0)

    def test_dangerous_call_eval_flagged(self):
        """Verify direct calls to eval() are caught as dangerous."""
        unsafe_code = "result = eval('2 + 2')\n"
        result = check_safety(unsafe_code)
        self.assertFalse(result["safe"])
        types = [i["type"] for i in result["issues"]]
        self.assertIn("dangerous_call", types)

    def test_dangerous_call_exec_flagged(self):
        """Verify direct calls to exec() are caught as dangerous."""
        unsafe_code = "exec('import os')\n"
        result = check_safety(unsafe_code)
        self.assertFalse(result["safe"])
        types = [i["type"] for i in result["issues"]]
        self.assertIn("dangerous_call", types)

    def test_system_command_is_flagged(self):
        """Verify os.system and similar attribute invocations are caught."""
        unsafe_code = "import os\nos.system('whoami')\n"
        result = check_safety(unsafe_code)
        self.assertFalse(result["safe"])
        types = [i["type"] for i in result["issues"]]
        self.assertTrue("dangerous_import" in types or "dangerous_attribute" in types)

    def test_destructive_file_operation_flagged(self):
        """Verify os.remove and destructive operations are flagged."""
        unsafe_code = "import os\nos.remove('/etc/hosts')\n"
        result = check_safety(unsafe_code)
        self.assertFalse(result["safe"])

    def test_dangerous_import_subprocess_flagged(self):
        """Verify importing subprocess is flagged."""
        code = "import subprocess\nsubprocess.run(['ls'])\n"
        result = check_safety(code)
        self.assertFalse(result["safe"])
        types = [i["type"] for i in result["issues"]]
        self.assertIn("dangerous_import", types)


def test_safe_code_placeholder():
    """Pytest-compatible wrapper."""
    case = TestSafetyChecker()
    case.test_safe_code()


def test_system_command_is_flagged_placeholder():
    """Pytest-compatible wrapper."""
    case = TestSafetyChecker()
    case.test_system_command_is_flagged()


def test_destructive_file_operation_is_flagged_placeholder():
    """Pytest-compatible wrapper."""
    case = TestSafetyChecker()
    case.test_destructive_file_operation_flagged()


if __name__ == "__main__":
    unittest.main()
