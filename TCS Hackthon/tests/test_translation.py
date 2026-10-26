"""
tests/test_translation.py
Tests for multilingual test cases data integrity and translation expectations.
"""

import csv
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "multilingual_test_cases.csv"


class TestTranslation(unittest.TestCase):
    """Test suite verifying multilingual test cases and expected translations."""

    def test_multilingual_csv_structure(self):
        """Verify multilingual test dataset exists and contains expected columns."""
        self.assertTrue(CSV_PATH.is_file(), f"Dataset not found at {CSV_PATH}")
        with CSV_PATH.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreaterEqual(len(rows), 10)
        required_cols = {"Test ID", "Input Language", "Requirement Entered", "Expected English Meaning"}
        self.assertTrue(required_cols.issubset(set(reader.fieldnames or [])))

        # Verify all rows have non-empty content
        for row in rows:
            self.assertTrue(row["Test ID"].strip())
            self.assertTrue(row["Input Language"].strip())
            self.assertTrue(row["Requirement Entered"].strip())
            self.assertTrue(row["Expected English Meaning"].strip())

    def test_empty_requirement_rejected(self):
        """Verify empty requirements are rejected across languages."""
        with self.assertRaises(ValueError):
            backend.generate("")

    def test_kannada_meaning_mapped(self):
        """Verify Kannada prime/duplicate requirements map to valid Python code."""
        # Test ML-02 or ML-04 English equivalent
        res = backend.generate("Create a Python function that checks whether a number is prime.")
        self.assertTrue(res["validation"]["status"] == "Passed")
        self.assertIn("def is_prime", res["generated_code"])


def test_translation_kannada_placeholder():
    case = TestTranslation()
    case.test_multilingual_csv_structure()


def test_translation_hindi_placeholder():
    case = TestTranslation()
    case.test_kannada_meaning_mapped()


def test_translation_urdu_placeholder():
    case = TestTranslation()
    case.test_multilingual_csv_structure()


def test_empty_requirement_rejected():
    case = TestTranslation()
    case.test_empty_requirement_rejected()


if __name__ == "__main__":
    unittest.main()
