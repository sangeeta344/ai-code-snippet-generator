"""
backend/correction.py

Automatic correction of LLM-generated Python code.

This module is invoked when the Validator and/or Safety Check stages of
the pipeline report problems with previously generated Python code. It
does NOT attempt to hand-patch the code with hardcoded string/regex
replacement rules. Instead, it packages up:

    1. The original natural-language requirement
    2. The offending generated code
    3. The validation errors reported against it
    4. Any safety issues reported against it

...into a single, strongly-worded correction prompt, and sends that
prompt to a local LLM served by Ollama. The LLM is responsible for
producing the corrected code; this module is responsible for prompt
construction, the HTTP call to Ollama, and robustly cleaning up
whatever text the LLM returns so that the rest of the pipeline
receives plain, executable Python source.

The corrected code returned by this module has NOT been re-validated
or re-safety-checked. The pipeline is expected to feed it back through
the Validator and Safety Check stages ("Validate again" in the overall
flow) before treating it as final.
"""

from __future__ import annotations

import os
import re
from typing import List, Optional

import requests


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_API_URL: str = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL: str = "qwen2.5-coder"

# Generous but bounded timeout (seconds) for the local Ollama call, since
# local code-model generations can be slow, especially on CPU.
OLLAMA_REQUEST_TIMEOUT: int = 120


def _get_model_name() -> str:
    """
    Resolve the Ollama model name to use.

    Reads the OLLAMA_MODEL environment variable if set and non-empty,
    otherwise falls back to DEFAULT_OLLAMA_MODEL. The model name is
    never hardcoded anywhere else in this module.
    """
    model = os.environ.get("OLLAMA_MODEL", "").strip()
    return model if model else DEFAULT_OLLAMA_MODEL


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _format_list(items: Optional[List[object]]) -> str:
    """
    Format a list of validation errors or safety issues into a readable
    block of text for inclusion in the correction prompt.

    Each item is rendered on its own line. Items may be plain strings or
    structured objects (e.g. dicts from the safety checker); both are
    rendered via str() so this function never raises on unexpected
    shapes.
    """
    if not items:
        return "None"

    lines = []
    for i, item in enumerate(items, start=1):
        lines.append(f"{i}. {item}")
    return "\n".join(lines)


def _build_correction_prompt(
    requirement: str,
    code: str,
    validation_errors: List[object],
    safety_issues: Optional[List[object]],
) -> str:
    """
    Build the full correction prompt sent to the LLM.

    The prompt includes the original requirement, the faulty generated
    code, the validation errors, and any safety issues, along with
    explicit instructions about what the corrected code must (and must
    not) do, and strict output-format requirements.
    """
    formatted_validation_errors = _format_list(validation_errors)
    formatted_safety_issues = _format_list(safety_issues)

    prompt = f"""You are an expert Python engineer fixing a previously generated code snippet.

Original requirement:
{requirement}

Generated code:
{code}

Validation errors:
{formatted_validation_errors}

Safety issues:
{formatted_safety_issues}

Instructions:
- Fix the identified problems listed above.
- Preserve the original functionality of the code.
- Follow the original requirement exactly.
- Do not remove required functionality merely to avoid an error.
- Do not introduce unnecessary libraries.
- Handle relevant edge cases.
- Do not use eval(), exec(), os.system(), unsafe subprocess usage, or other dangerous constructs, unless the original requirement explicitly and legitimately requires something that needs special handling.
- Return ONLY valid, complete, runnable Python source code implementing the fix.
- Do not return Markdown.
- Do not return ```python fences or any other code fences.
- Do not return explanations, commentary, or reasoning of any kind.
- Do not return JSON.
- Your entire response must be valid Python source code and nothing else.
"""
    return prompt


# ---------------------------------------------------------------------------
# Ollama API call
# ---------------------------------------------------------------------------

def _call_ollama(prompt: str, model: str) -> str:
    """
    Send a correction prompt to the local Ollama API and return the raw
    text of the model's response.

    Raises:
        RuntimeError: if the request to Ollama fails, times out, or the
            response does not contain the expected "response" field.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=OLLAMA_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"Failed to reach Ollama at {OLLAMA_API_URL} using model "
            f"'{model}': {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Ollama returned a non-JSON response: {exc}"
        ) from exc

    raw_text = data.get("response")
    if raw_text is None:
        raise RuntimeError(
            "Ollama response JSON did not contain a 'response' field: "
            f"{data!r}"
        )

    return raw_text


# ---------------------------------------------------------------------------
# Robust response cleanup
# ---------------------------------------------------------------------------

_CODE_FENCE_PATTERN = re.compile(
    r"```(?:python|py)?\s*\n?(.*?)```",
    re.DOTALL | re.IGNORECASE,
)


def _strip_code_fences(text: str) -> str:
    """
    Extract code from a Markdown-style code fence if present.

    If the LLM wraps its answer like:

```python
        def example():
            pass
```

    this returns just the inner code. If multiple fenced blocks are
    present, they are concatenated in order, separated by a blank line.
    If no fences are found, the original text is returned unchanged.
    """
    matches = _CODE_FENCE_PATTERN.findall(text)
    if not matches:
        return text

    blocks = [m.strip("\n") for m in matches]
    return "\n\n".join(blocks)


def _strip_leading_language_tag(text: str) -> str:
    """
    Remove a stray leading 'python' or 'py' language tag that some
    models emit on its own line even without full code fences.
    """
    lines = text.split("\n")
    if lines and lines[0].strip().lower() in {"python", "py"}:
        return "\n".join(lines[1:])
    return text


def _clean_llm_code_response(raw_text: str) -> str:
    """
    Normalize whatever the LLM returned into plain Python source code.

    Handles common misbehavior:
      - Code wrapped in ```python ... ``` or ``` ... ``` fences
      - A stray leading 'python' language tag with no fences
      - Leading/trailing whitespace or blank lines
    """
    if raw_text is None:
        return ""

    text = raw_text.strip()
    text = _strip_code_fences(text)
    text = _strip_leading_language_tag(text)
    text = text.strip()

    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def correct_code(
    requirement: str,
    code: str,
    validation_errors: List[object],
    safety_issues: Optional[List[object]] = None,
) -> str:
    """
    Ask the local LLM (via Ollama) to correct previously generated
    Python code based on reported validation errors and/or safety
    issues.

    This function does NOT attempt any manual/hardcoded repair of the
    code itself. It builds a correction prompt containing the original
    requirement, the faulty code, the validation errors, and any safety
    issues, sends that prompt to Ollama, and returns the corrected
    source code extracted from the model's response.

    The returned code is NOT guaranteed to be valid or safe. The caller
    is expected to run it back through the Validator and Safety Check
    stages before treating it as final, per the overall pipeline flow.

    Args:
        requirement: The original natural-language software requirement.
        code: The previously generated Python code that needs fixing.
        validation_errors: A list of validation errors reported against
            `code`. Items may be strings or structured objects; they are
            rendered via str() in the prompt.
        safety_issues: An optional list of safety issues reported
            against `code` (e.g. from a safety-screening module). May be
            None or empty if there were no safety issues.

    Returns:
        The corrected Python source code as a plain string, with any
        Markdown code fences or stray language tags stripped.

    Raises:
        RuntimeError: if the call to the Ollama API fails or returns an
            unexpected/invalid response.
    """
    model = _get_model_name()
    prompt = _build_correction_prompt(
        requirement=requirement,
        code=code,
        validation_errors=validation_errors,
        safety_issues=safety_issues,
    )

    raw_response = _call_ollama(prompt, model)
    corrected_code = _clean_llm_code_response(raw_response)

    return corrected_code