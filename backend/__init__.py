"""
backend package initialization.
Exports key generator and validation pipeline APIs.
"""

from backend.generator import generate, get_active_provider_info, test_api_connection
from backend.pipeline import validate_code_pipeline
from backend.safety import check_safety
from backend.validator import validate_code, validate_structure, validate_syntax
from backend.rag import retrieve_context

__all__ = [
    "generate",
    "get_active_provider_info",
    "test_api_connection",
    "validate_code_pipeline",
    "check_safety",
    "validate_code",
    "validate_structure",
    "validate_syntax",
    "retrieve_context",
]
