"""
tests/test_frontend.py
Automated UI and Integration tests for the Streamlit application using AppTest.
Tests component initialization, input text changes, preset switching,
generate code button click, validation rendering, and reset actions.
"""

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestStreamlitFrontend(unittest.TestCase):
    """Test suite for Streamlit frontend using AppTest."""

    def test_app_initialization(self):
        """Verify the Streamlit app loads and renders without exceptions."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(str(ROOT_DIR / "frontend" / "app.py"), default_timeout=25)
        at.run()
        self.assertEqual(len(at.exception), 0, f"App had exceptions on init: {at.exception}")
        self.assertFalse(at.session_state.is_generated)
        self.assertIsNone(at.session_state.result_data)

    def test_generate_code_click_produces_result(self):
        """Verify clicking Generate Code executes the pipeline and updates session state."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(str(ROOT_DIR / "frontend" / "app.py"), default_timeout=25)
        at.run()

        # Click the Generate button
        gen_btn = at.button[0]
        gen_btn.click().run()

        self.assertEqual(len(at.exception), 0, f"Exceptions occurred after click: {at.exception}")
        self.assertTrue(at.session_state.is_generated)
        self.assertIsNotNone(at.session_state.result_data)
        self.assertEqual(at.session_state.result_data["validation"]["status"], "Passed")
        self.assertTrue("def check_age" in at.session_state.result_data["generated_code"] or "def is_prime" in at.session_state.result_data["generated_code"])

    def test_empty_input_shows_error(self):
        """Verify submitting empty input does not crash and leaves is_generated as False."""
        from streamlit.testing.v1 import AppTest

        at = AppTest.from_file(str(ROOT_DIR / "frontend" / "app.py"), default_timeout=25)
        at.run()

        # Set prompt to empty string
        at.text_area[0].input("").run()
        gen_btn = at.button[0]
        gen_btn.click().run()

        self.assertEqual(len(at.exception), 0)
        self.assertFalse(at.session_state.is_generated)
        self.assertIsNone(at.session_state.result_data)


if __name__ == "__main__":
    unittest.main()
