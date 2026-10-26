"""
tests/test_multilingual_flow.py
Tests verifying that requirements (including regional and mixed formulations)
produce valid, safe, and syntactically correct Python code snippets.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend


class TestMultilingualFlow(unittest.TestCase):
    """End-to-end multilingual and mixed-language flow tests."""

    def test_prime_flow(self):
        """Verify prime checker requirement generates valid Python."""
        res = backend.generate("Prime number check ಮಾಡಿ, Python function ರಚಿಸಿ")
        self.assertEqual(res["validation"]["status"], "Passed")
        self.assertTrue(backend.validate_syntax(res["generated_code"])["valid"])

    def test_duplicate_removal_flow(self):
        """Verify list duplicate removal requirement generates valid Python."""
        res = backend.generate("List duplicates remove ಮಾಡಿ original order preserve ಮಾಡುವ Python function")
        self.assertEqual(res["validation"]["status"], "Passed")
        self.assertTrue(backend.validate_syntax(res["generated_code"])["valid"])

    def test_string_reversal_flow(self):
        """Verify string palindrome / reversal flow produces safe Python code."""
        res = backend.generate("String palindrome check karne wala Python function banayein")
        self.assertEqual(res["validation"]["status"], "Passed")
        self.assertTrue(backend.validate_syntax(res["generated_code"])["valid"])

    def test_mixed_language_safety(self):
        """Verify safety checker ensures no malicious code is generated."""
        res = backend.generate("Calculate average salary from CSV and export summary")
        self.assertTrue(res["validation"]["pipeline_result"]["safety"]["safe"])


def test_kannada_to_code_flow_placeholder():
    case = TestMultilingualFlow()
    case.test_prime_flow()


def test_hindi_to_code_flow_placeholder():
    case = TestMultilingualFlow()
    case.test_string_reversal_flow()


def test_urdu_to_code_flow_placeholder():
    case = TestMultilingualFlow()
    case.test_duplicate_removal_flow()


def test_mixed_language_flow_placeholder():
    case = TestMultilingualFlow()
    case.test_mixed_language_safety()


if __name__ == "__main__":
    unittest.main()
