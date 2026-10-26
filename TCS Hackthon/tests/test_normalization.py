"""
tests/test_normalization.py
Tests for requirement normalization and structured schema extraction.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend


class TestNormalization(unittest.TestCase):
    """Test suite verifying requirement normalization into structured schema."""

    def test_normalized_requirement_contains_task(self):
        """Verify structured output identifies the primary intent/task."""
        res = backend.generate("Create a Python function to calculate the average of a list of numbers.")
        analysis = res.get("analysis", {})
        self.assertIn("intent", analysis)
        self.assertTrue(len(analysis["intent"]) > 0)

    def test_normalized_requirement_contains_input_output(self):
        """Verify expected input and output are extracted."""
        res = backend.generate("Create a Python function that checks whether two strings are anagrams of each other.")
        analysis = res.get("analysis", {})
        self.assertIn("inputs", analysis)
        self.assertIn("outputs", analysis)
        self.assertTrue(len(analysis["inputs"]) > 0)
        self.assertTrue(len(analysis["outputs"]) > 0)

    def test_normalization_identifies_edge_cases(self):
        """Verify edge cases and constraints are captured."""
        res = backend.generate("Create a Python function to generate Fibonacci sequence up to n terms.")
        analysis = res.get("analysis", {})
        self.assertIn("edge_cases", analysis)
        self.assertIsInstance(analysis["edge_cases"], list)
        self.assertGreater(len(analysis["edge_cases"]), 0)


def test_normalized_requirement_contains_task():
    case = TestNormalization()
    case.test_normalized_requirement_contains_task()


def test_normalized_requirement_contains_input_output():
    case = TestNormalization()
    case.test_normalized_requirement_contains_input_output()


def test_normalization_identifies_edge_cases():
    case = TestNormalization()
    case.test_normalization_identifies_edge_cases()


if __name__ == "__main__":
    unittest.main()
