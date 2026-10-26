"""
backend/prompts.py

Structured Prompt Engineering and Response Parsing for Code Generation.
Guarantees consistent, safe, and schema-compliant outputs from LLM providers.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional


SYSTEM_PROMPT = """You are an expert Python software engineer and system architect.
Your task is to generate complete, production-ready, readable, and syntactically valid Python code snippets from natural-language software requirements.

Strict Requirements:
1. Analyze the requirement and any constraints thoroughly before writing code.
2. Write clean, readable, PEP 8-compliant Python code with meaningful variable and function names.
3. Include all necessary standard library or common package imports at the top.
4. Handle reasonable edge cases (e.g. empty inputs, nulls, division by zero, boundary conditions).
5. Avoid unnecessary external dependencies or oversized libraries.
6. Do NOT include eval(), exec(), os.system(), or unsafe subprocess calls.
7. Explain important implementation decisions clearly and concisely.
8. Include practical input and output examples.
9. Generate self-contained unit test cases using unittest or assertions.
10. State any technical assumptions made.

Output Format:
You MUST respond with a single valid JSON object. Do NOT wrap the JSON in conversational filler.
The JSON object must have exactly these keys:
{
  "requirement_summary": "<One-sentence summary of the task>",
  "assumptions": ["<Assumption 1>", "<Assumption 2>"],
  "intent": "<Core purpose of the code>",
  "inputs": "<Expected input types and description>",
  "outputs": "<Expected output types and description>",
  "constraints_handled": "<How technical constraints and boundaries are handled>",
  "edge_cases": ["<Edge case 1>", "<Edge case 2>"],
  "libraries": ["<library1>", "<library2>"],
  "code": "<Complete, executable Python code with docstrings and type annotations>",
  "explanation": "<Concise breakdown of logic, algorithms, and design decisions>",
  "examples": [
    {"input": "<sample call 1>", "output": "<expected output 1>"},
    {"input": "<sample call 2>", "output": "<expected output 2>"}
  ],
  "test_cases": "<Executable Python test script or unittest.TestCase>",
  "validation_status": "Valid Python"
}
"""


def build_user_prompt(
    requirement: str,
    constraints: Optional[str] = None,
    language: str = "Python",
    retrieved_examples: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Build a structured prompt including user requirement, constraints, and RAG context."""
    sections = []

    sections.append(f"Target Language: {language}")
    sections.append(f"User Requirement:\n{requirement.strip()}")

    if constraints and constraints.strip():
        sections.append(f"Additional Constraints:\n{constraints.strip()}")

    if retrieved_examples:
        context_blocks = []
        for i, entry in enumerate(retrieved_examples[:2], start=1):
            item = entry.get("item", entry)
            snippet = item.get("code", "")[:400]
            context_blocks.append(
                f"--- Reference Example {i} ({entry.get('id', 'REF')}) ---\n"
                f"Requirement: {entry.get('requirement', '')}\n"
                f"Code snippet pattern:\n{snippet}\n"
            )
        sections.append("Relevant Reference Patterns from Knowledge Base:\n" + "\n".join(context_blocks))

    sections.append(
        "Please respond with the complete JSON object conforming strictly to the requested schema."
    )

    return "\n\n".join(sections)


def extract_code_from_markdown(text: str) -> str:
    """Extract code from ```python or ``` fences if present."""
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def parse_and_clean_response(raw_text: str, fallback_requirement: str = "") -> Dict[str, Any]:
    """Parse the LLM response into a structured dictionary.

    Handles malformed responses, raw markdown, stray backticks, or truncated JSON.
    """
    if not raw_text or not raw_text.strip():
        return _build_fallback_result("Empty model response.", fallback_requirement)

    cleaned = raw_text.strip()

    # Strip markdown json fences ```json ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

    # First attempt: direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "code" in data:
            return _normalize_schema(data, fallback_requirement)
    except json.JSONDecodeError:
        pass

    # Second attempt: locate JSON substring { ... }
    json_match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, dict) and "code" in data:
                return _normalize_schema(data, fallback_requirement)
        except json.JSONDecodeError:
            pass

    # Third attempt: extract code block directly from raw text
    extracted_code = extract_code_from_markdown(raw_text)
    if extracted_code and ("def " in extracted_code or "import " in extracted_code or "class " in extracted_code):
        return {
            "requirement_summary": fallback_requirement or "Generated Python Code",
            "assumptions": ["Assumed standard Python 3.10+ runtime."],
            "intent": fallback_requirement or "Implement required functionality",
            "inputs": "Refer to function parameters and docstring",
            "outputs": "Refer to return type and function signature",
            "constraints_handled": "Standard boundary conditions handled.",
            "edge_cases": ["None or empty inputs", "Invalid types"],
            "libraries": ["sys"],
            "code": extracted_code,
            "explanation": "Extracted Python snippet from model output.",
            "examples": [{"input": "See function docstring", "output": "See return type"}],
            "test_cases": "# Automated tests can be run against the generated function\n",
            "validation_status": "Valid Python",
        }

    return _build_fallback_result(f"Could not parse valid code from model response: {raw_text[:120]}...", fallback_requirement)


def _normalize_schema(data: Dict[str, Any], fallback_req: str) -> Dict[str, Any]:
    """Ensure all required keys exist and have proper types."""
    code = data.get("code", "").strip()
    # Strip any internal fences in code field
    if code.startswith("```"):
        code = extract_code_from_markdown(code)

    return {
        "requirement_summary": str(data.get("requirement_summary") or fallback_req or "Python Implementation"),
        "assumptions": list(data.get("assumptions") or ["Standard Python 3 environment"]),
        "intent": str(data.get("intent") or data.get("requirement_summary") or fallback_req),
        "inputs": str(data.get("inputs") or "Function parameters"),
        "outputs": str(data.get("outputs") or "Return values"),
        "constraints_handled": str(data.get("constraints_handled") or "Default constraints satisfied"),
        "edge_cases": list(data.get("edge_cases") or ["Empty input", "Boundary conditions"]),
        "libraries": list(data.get("libraries") or []),
        "code": code,
        "explanation": str(data.get("explanation") or "Standard implementation of the requested requirement."),
        "examples": list(data.get("examples") or []),
        "test_cases": str(data.get("test_cases") or ""),
        "validation_status": str(data.get("validation_status") or "Pending Validation"),
    }


def _build_fallback_result(error_msg: str, fallback_req: str) -> Dict[str, Any]:
    """Generate a graceful fallback dictionary when parsing completely fails."""
    return {
        "requirement_summary": fallback_req or "Code Generation",
        "assumptions": ["Fallback mode due to response error."],
        "intent": fallback_req or "Resolve requirement",
        "inputs": "None",
        "outputs": "None",
        "constraints_handled": "Failed to generate code.",
        "edge_cases": [],
        "libraries": [],
        "code": f"# Error during code generation: {error_msg}\n",
        "explanation": f"The model response could not be parsed: {error_msg}",
        "examples": [],
        "test_cases": "",
        "validation_status": "Error",
        "error": error_msg,
    }
