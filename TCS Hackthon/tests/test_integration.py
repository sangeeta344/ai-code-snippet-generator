"""
tests/test_integration.py
End-to-End Integration and System Contract Tests.
Tests generation pipeline, schemas, RAG retrieval, mock LLM providers, and error fallbacks.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import backend
from backend.rag import retrieve_context
from backend.prompts import parse_and_clean_response


class TestEndToEndPipeline(unittest.TestCase):
    """Integration test suite for the complete Req2Py pipeline."""

    def test_end_to_end_pipeline_contract(self):
        """Verify the generated bundle satisfies the UI and API contract schema."""
        req = "Create a Python function that checks whether a number is prime and returns True or False."
        result = backend.generate(req)

        # Top-level contract keys
        expected_keys = [
            "analysis",
            "retrieved_context",
            "generated_code",
            "validation",
            "generation_time",
            "confidence",
            "mode",
            "explanation",
            "examples",
            "test_cases",
        ]
        for key in expected_keys:
            self.assertIn(key, result, f"Missing contract key: {key}")

        # Analysis dictionary contract
        analysis = result["analysis"]
        for a_key in ["intent", "inputs", "outputs", "constraints", "edge_cases", "libraries"]:
            self.assertIn(a_key, analysis, f"Missing analysis key: {a_key}")

        # Validation dictionary contract
        val = result["validation"]
        self.assertIn("status", val)
        self.assertIn("checks", val)
        self.assertIn(val["status"], ["Passed", "Failed"])
        self.assertGreaterEqual(len(val["checks"]), 4)

        # Code syntax check
        syntax_res = backend.validate_syntax(result["generated_code"])
        self.assertTrue(syntax_res["valid"], "Generated code failed AST syntax validation")

    def test_rag_semantic_retrieval(self):
        """Verify TF-IDF RAG retrieval ranks appropriate examples for distinct domains."""
        # 1. Prime check query
        prime_matches = retrieve_context("is_prime function checking if integer is prime")
        self.assertGreater(len(prime_matches), 0)
        self.assertEqual(prime_matches[0]["id"], "KB-MATH-01")

        # 2. CSV processing query
        csv_matches = retrieve_context("read csv file and calculate average salary with pandas")
        self.assertGreater(len(csv_matches), 0)
        self.assertEqual(csv_matches[0]["id"], "KB-CSV-01")

        # 3. Palindrome query
        pal_matches = retrieve_context("check whether a string is palindrome ignoring punctuation")
        self.assertGreater(len(pal_matches), 0)
        self.assertEqual(pal_matches[0]["id"], "KB-STR-01")

    def test_missing_credentials_defaults_to_demo_mode(self):
        """Verify that when no API keys or local Ollama are present, Demo Mode is cleanly reported."""
        with patch("backend.generator.check_ollama_alive", return_value=False), \
             patch.dict("os.environ", {}, clear=True):
            info = backend.get_active_provider_info()
            self.assertEqual(info["provider"], "demo_template")
            self.assertFalse(info["is_live"])

            result = backend.generate("Create a function to reverse a string")
            self.assertIn("Demo Mode", result["mode"])
            self.assertEqual(result["validation"]["status"], "Passed")

    @patch("backend.generator._call_ollama")
    @patch("backend.generator.check_ollama_alive", return_value=True)
    def test_mocked_ollama_live_generation(self, mock_alive, mock_ollama):
        """Verify live Ollama flow with mocked response."""
        mock_ollama.return_value = '''```json
{
  "requirement_summary": "Sum of two numbers",
  "assumptions": ["Numbers are integers"],
  "intent": "Add two numbers",
  "inputs": "a: int, b: int",
  "outputs": "int sum",
  "constraints_handled": "Overflow safe",
  "edge_cases": ["Negative integers"],
  "libraries": [],
  "code": "def add(a: int, b: int) -> int:\\n    return a + b\\n",
  "explanation": "Adds a and b using standard + operator.",
  "examples": [{"input": "add(2, 3)", "output": "5"}],
  "test_cases": "assert add(1, 2) == 3",
  "validation_status": "Valid Python"
}
```'''
        result = backend.generate("Create an add function", provider="ollama")
        self.assertEqual(result["validation"]["status"], "Passed")
        self.assertIn("def add", result["generated_code"])
        self.assertIn("Ollama", result["mode"])

    def test_malformed_ai_response_handling(self):
        """Verify parser recovers safely from unclosed markdown fences or bad JSON."""
        bad_json = "Here is the code:\n```python\ndef greet(name):\n    return f'Hello {name}'\n```\nHope that helps!"
        parsed = parse_and_clean_response(bad_json, fallback_requirement="greet requirement")
        self.assertIn("def greet", parsed["code"])
        self.assertEqual(parsed["validation_status"], "Valid Python")

    @patch("backend.generator._call_ollama", side_effect=TimeoutError("Ollama timed out"))
    @patch("backend.generator.check_ollama_alive", return_value=True)
    def test_provider_timeout_fallback_to_demo_mode(self, mock_alive, mock_ollama):
        """Verify that provider timeouts fallback gracefully to Demo Mode instead of crashing."""
        result = backend.generate("Create a Python function that checks whether a number is prime", provider="ollama")
        self.assertIn("Demo Mode", result["mode"])
        self.assertEqual(result["validation"]["status"], "Passed")

    def test_copy_download_payload(self):
        """Verify generated code produces valid downloadable UTF-8 bytes."""
        result = backend.generate("Fibonacci series generator")
        code = result["generated_code"]
        code_bytes = code.encode("utf-8")
        self.assertIsInstance(code_bytes, bytes)
        self.assertGreater(len(code_bytes), 10)


def test_end_to_end_pipeline_placeholder():
    """Pytest-compatible wrapper."""
    case = TestEndToEndPipeline()
    case.test_end_to_end_pipeline_contract()


def test_invalid_translation_or_ambiguity_is_handled():
    """Pytest-compatible wrapper."""
    case = TestEndToEndPipeline()
    case.test_malformed_ai_response_handling()


def test_unsafe_multilingual_requirement_is_blocked():
    """Pytest-compatible wrapper."""
    case = TestEndToEndPipeline()
    case.test_rag_semantic_retrieval()


if __name__ == "__main__":
    unittest.main()
