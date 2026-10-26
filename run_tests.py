"""
run_tests.py
Automated Test Runner for the AI-Powered Code Snippet Generator.
Discovers and executes all unit and integration tests across the project.
"""

import sys
import time
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_all_tests():
    """Discover and execute all test suites with deterministic offline test isolation."""
    import os

    # Isolate test suite from live cloud API calls per Phase 3.F specification:
    # "Use mocked AI responses for automated tests so that tests do not require paid API calls."
    os.environ["CODEFORGE_TEST_MODE"] = "1"
    env_keys_to_restore = {}
    for key in ("GEMINI_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "LLM_API_KEY"):
        if key in os.environ:
            env_keys_to_restore[key] = os.environ.pop(key)

    start_time = time.perf_counter()
    try:
        loader = unittest.TestLoader()

        test_dirs = [
            PROJECT_ROOT / "TCS Hackthon" / "tests",
        ]

        suite = unittest.TestSuite()
        for tdir in test_dirs:
            if tdir.is_dir():
                discovered = loader.discover(start_dir=str(tdir), pattern="test_*.py")
                suite.addTests(discovered)

        print("=" * 70)
        print("CODEFORGE AI — AUTOMATED TEST SUITE RUNNER")
        print(f"Total Test Cases Discovered: {suite.countTestCases()}")
        print("=" * 70)

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        elapsed = time.perf_counter() - start_time
        print("=" * 70)
        print(f"TEST EXECUTION SUMMARY:")
        print(f"  Ran: {result.testsRun} tests in {elapsed:.3f} seconds")
        print(f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"  Failures: {len(result.failures)}")
        print(f"  Errors: {len(result.errors)}")
        print("=" * 70)

        return 0 if result.wasSuccessful() else 1
    finally:
        # Restore environment variables
        os.environ.update(env_keys_to_restore)


if __name__ == "__main__":
    sys.exit(run_all_tests())
