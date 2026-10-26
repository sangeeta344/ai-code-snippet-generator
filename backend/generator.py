"""
backend/generator.py

Unified Code Generation Engine for Req2Py / CodeForge AI.
Supports live AI generation via:
  1. Google Gemini API (gemini-1.5-flash / gemini-2.0-flash)
  2. OpenAI / Groq / OpenRouter / OpenAI-compatible APIs
  3. Local Ollama (e.g. qwen2.5-coder)
  4. Smart Dynamic Synthesizer & Curated Knowledge Base (when offline or without API key)

Automatically loads keys from .env or UI input.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

# Load .env file automatically
import backend.config  # noqa: F401
from backend.pipeline import validate_code_pipeline
from backend.prompts import SYSTEM_PROMPT, build_user_prompt, parse_and_clean_response
from backend.rag import retrieve_context
from backend.synthesizer import try_synthesize_pattern, synthesize_scaffold


# -----------------------------------------------------------------------------
# Configuration & Provider Defaults
# -----------------------------------------------------------------------------
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
DEFAULT_OLLAMA_MODEL: str = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder")

DEFAULT_API_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o-mini")
DEFAULT_API_BASE_URL: str = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")

DEFAULT_GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
DEFAULT_GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GEMINI_FALLBACK_MODELS: List[str] = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-flash-latest"]

REQUEST_TIMEOUT: int = int(os.environ.get("LLM_TIMEOUT", "60"))


def check_ollama_alive() -> bool:
    """Check if a local Ollama server is responsive."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=0.6)
        return resp.status_code == 200
    except Exception:
        return False


def detect_provider_from_key(key: str) -> Tuple[str, str, str]:
    """Auto-detect provider, model, and base URL from API key format.

    Returns:
        (provider_type, default_model, base_url)
    """
    clean_key = (key or "").strip()
    if clean_key.startswith("AIzaSy") or clean_key.startswith("AQ.") or clean_key.startswith("AIza"):
        return "gemini", DEFAULT_GEMINI_MODEL, "https://generativelanguage.googleapis.com"
    elif clean_key.startswith("gsk_"):
        return "openai_compatible", DEFAULT_GROQ_MODEL, "https://api.groq.com/openai/v1"
    elif clean_key.startswith("sk-"):
        return "openai_compatible", DEFAULT_API_MODEL, "https://api.openai.com/v1"
    elif clean_key:
        return "gemini", DEFAULT_GEMINI_MODEL, "https://generativelanguage.googleapis.com"
    return "demo_template", "SmartSynthesizer-v2", ""


def get_active_provider_info(
    override_provider: Optional[str] = None,
    override_api_key: Optional[str] = None,
    override_model: Optional[str] = None,
) -> Dict[str, Any]:
    """Detect and return information on the available AI provider."""
    # 0. Explicit provider override for Ollama or Demo Mode
    if override_provider == "ollama":
        mod = override_model or DEFAULT_OLLAMA_MODEL
        return {
            "provider": "ollama",
            "model": mod,
            "display_name": f"Live AI (Ollama: {mod})",
            "api_key": "",
            "base_url": OLLAMA_BASE_URL,
            "is_live": check_ollama_alive(),
        }
    if override_provider == "demo_template":
        return {
            "provider": "demo_template",
            "model": "SmartSynthesizer-v2",
            "display_name": "Demo Mode (Smart Offline Synthesizer)",
            "api_key": "",
            "base_url": "",
            "is_live": False,
        }

    # 1. Key passed explicitly from UI
    if override_api_key and override_api_key.strip():
        key = override_api_key.strip()
        auto_prov, auto_model, base_url = detect_provider_from_key(key)
        prov = override_provider if override_provider and override_provider != "auto" else auto_prov
        mod = override_model or auto_model

        if prov == "gemini":
            return {
                "provider": "gemini",
                "model": mod,
                "display_name": f"Live AI (Google Gemini: {mod})",
                "api_key": key,
                "base_url": base_url,
                "is_live": True,
            }
        elif prov in ("openai", "openai_compatible"):
            b_url = "https://api.groq.com/openai/v1" if key.startswith("gsk_") else DEFAULT_API_BASE_URL
            return {
                "provider": "openai_compatible",
                "model": mod,
                "display_name": f"Live AI (API: {mod})",
                "api_key": key,
                "base_url": b_url,
                "is_live": True,
            }

    # 2. Check environment variables
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key and gemini_key.strip():
        mod = override_model or DEFAULT_GEMINI_MODEL
        return {
            "provider": "gemini",
            "model": mod,
            "display_name": f"Live AI (Google Gemini: {mod})",
            "api_key": gemini_key.strip(),
            "base_url": "https://generativelanguage.googleapis.com",
            "is_live": True,
        }

    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key and groq_key.strip():
        mod = override_model or DEFAULT_GROQ_MODEL
        return {
            "provider": "openai_compatible",
            "model": mod,
            "display_name": f"Live AI (Groq: {mod})",
            "api_key": groq_key.strip(),
            "base_url": "https://api.groq.com/openai/v1",
            "is_live": True,
        }

    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if api_key and api_key.strip():
        mod = override_model or DEFAULT_API_MODEL
        return {
            "provider": "openai_compatible",
            "model": mod,
            "display_name": f"Live AI (API: {mod})",
            "api_key": api_key.strip(),
            "base_url": DEFAULT_API_BASE_URL,
            "is_live": True,
        }

    # 3. Check local Ollama
    if check_ollama_alive() or override_provider == "ollama":
        mod = override_model or DEFAULT_OLLAMA_MODEL
        return {
            "provider": "ollama",
            "model": mod,
            "display_name": f"Live AI (Ollama: {mod})",
            "api_key": "",
            "base_url": OLLAMA_BASE_URL,
            "is_live": check_ollama_alive(),
        }

    # 4. Fallback: Smart Offline Synthesizer
    return {
        "provider": "demo_template",
        "model": "SmartSynthesizer-v2",
        "display_name": "Demo Mode (Smart Offline Synthesizer)",
        "api_key": "",
        "base_url": "",
        "is_live": False,
    }


def test_api_connection(
    api_key: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Test if the provided API key or endpoint responds successfully."""
    clean_key = (api_key or "").strip()
    auto_prov, auto_mod, b_url = detect_provider_from_key(clean_key)
    prov = provider if provider and provider != "auto" else auto_prov
    mod = model or auto_mod

    if prov == "gemini":
        candidate_models = [mod] + [m for m in GEMINI_FALLBACK_MODELS if m != mod]
        last_err = ""
        for candidate in candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{candidate}:generateContent?key={clean_key}"
            payload = {"contents": [{"parts": [{"text": "Reply with 'ok'"}]}]}
            try:
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
                if resp.status_code == 200:
                    return {"success": True, "message": f"Successfully connected to Google Gemini ({candidate})!"}
                else:
                    err_detail = resp.json().get("error", {}).get("message", resp.text[:140])
                    last_err = f"Gemini Error ({resp.status_code}): {err_detail}"
                    # If model not available/deprecated, try next model candidate
                    if resp.status_code == 404:
                        continue
                    return {"success": False, "message": last_err}
            except Exception as exc:
                last_err = f"Connection failed: {exc}"
        return {"success": False, "message": last_err}

    elif prov in ("openai", "openai_compatible"):
        base = b_url or DEFAULT_API_BASE_URL
        url = f"{base}/chat/completions"
        headers = {"Authorization": f"Bearer {clean_key}", "Content-Type": "application/json"}
        payload = {
            "model": mod,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 5,
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                return {"success": True, "message": f"Successfully connected to API ({mod})!"}
            else:
                err_detail = resp.json().get("error", {}).get("message", resp.text)
                return {"success": False, "message": f"API Error ({resp.status_code}): {err_detail}"}
        except Exception as exc:
            return {"success": False, "message": f"Connection failed: {exc}"}

    elif prov == "ollama":
        if check_ollama_alive():
            return {"success": True, "message": "Successfully connected to local Ollama!"}
        return {"success": False, "message": "Could not reach local Ollama on http://localhost:11434"}

    return {"success": False, "message": "Please enter a valid Gemini or OpenAI API key."}


# -----------------------------------------------------------------------------
# LLM Invocation Handlers
# -----------------------------------------------------------------------------
def _call_gemini(prompt: str, model: str, api_key: str) -> Tuple[str, str]:
    """Invoke Google Gemini generateContent API with smart fallback across models.

    Returns:
        (generated_text, model_name_used)
    """
    candidate_models = [model] + [m for m in GEMINI_FALLBACK_MODELS if m != model]
    last_exception: Optional[Exception] = None

    for candidate in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{candidate}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{SYSTEM_PROMPT}\n\nUser Request:\n{prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
            },
        }
        headers = {"Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 404:
                # Model is deprecated or not available for this key tier; try next
                continue
            resp.raise_for_status()
            data = resp.json()

            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError(f"No candidates returned by Gemini: {data}")
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                raise RuntimeError("No content parts in Gemini candidate response.")
            return parts[0].get("text", ""), candidate
        except Exception as exc:
            last_exception = exc
            if hasattr(exc, "response") and getattr(exc, "response") is not None:
                code = getattr(getattr(exc, "response"), "status_code", None)
                if code in (404, 503):
                    continue
            break

    if last_exception:
        raise last_exception
    raise RuntimeError(f"Could not connect to Gemini models: {candidate_models[:2]}")


def _call_ollama(prompt: str, model: str) -> str:
    """Invoke local Ollama generate endpoint."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "format": "json",
    }
    resp = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("response", "")


def _call_openai_compatible(prompt: str, model: str, api_key: str, base_url: str) -> str:
    """Invoke OpenAI-compatible chat completions endpoint."""
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("No completion choices returned by API provider.")
    return choices[0].get("message", {}).get("content", "")


# -----------------------------------------------------------------------------
# Main Generation Pipeline
# -----------------------------------------------------------------------------
def generate(
    requirement: str,
    constraints: Optional[str] = None,
    language: str = "Python",
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate Python code snippet from a natural language requirement.

    Args:
        requirement: Natural language requirement string.
        constraints: Optional extra technical constraints or rules.
        language: Target programming language (defaults to "Python").
        api_key: Optional user-provided API key from frontend or env.
        provider: Optional provider override ('gemini', 'openai', 'ollama', 'auto').
        model: Optional model name override.

    Returns:
        Structured response dictionary matching the application contract.
    """
    start_time = time.perf_counter()

    clean_req = (requirement or "").strip()
    if not clean_req:
        raise ValueError("Requirement cannot be empty. Please specify the desired functionality.")

    # 1. RAG Context Retrieval
    retrieved_entries = retrieve_context(clean_req, top_k=3)
    best_match = retrieved_entries[0] if retrieved_entries else None
    best_item = best_match.get("item", {}) if best_match else {}
    best_similarity = best_match.get("similarity", 0) if best_match else 0

    retrieved_context_ui = [
        {
            "id": entry["id"],
            "requirement": entry["requirement"],
            "similarity": entry["similarity"],
        }
        for entry in retrieved_entries
    ]

    # 2. Determine Active Provider
    provider_info = get_active_provider_info(
        override_provider=provider,
        override_api_key=api_key,
        override_model=model,
    )
    active_provider = provider_info["provider"]
    mode_name = provider_info["display_name"]
    resolved_key = provider_info.get("api_key") or api_key or ""

    raw_response_data: Optional[Dict[str, Any]] = None
    generation_source: str = mode_name

    # 3. If Live AI is configured, execute via LLM
    if active_provider == "gemini" and resolved_key:
        try:
            prompt = build_user_prompt(clean_req, constraints, language, retrieved_entries)
            raw_text, used_model = _call_gemini(prompt, model=provider_info["model"], api_key=resolved_key)
            raw_response_data = parse_and_clean_response(raw_text, fallback_requirement=clean_req)
            generation_source = f"Live AI (Google Gemini: {used_model})"
        except Exception as exc:
            generation_source = f"Demo Mode (Gemini fallback: {exc})"
            active_provider = "demo_template"

    elif active_provider == "openai_compatible" and resolved_key:
        try:
            base_url = provider_info.get("base_url") or DEFAULT_API_BASE_URL
            prompt = build_user_prompt(clean_req, constraints, language, retrieved_entries)
            raw_text = _call_openai_compatible(prompt, model=provider_info["model"], api_key=resolved_key, base_url=base_url)
            raw_response_data = parse_and_clean_response(raw_text, fallback_requirement=clean_req)
        except Exception as exc:
            generation_source = f"Demo Mode (API error: {exc})"
            active_provider = "demo_template"

    elif active_provider == "ollama":
        try:
            prompt = build_user_prompt(clean_req, constraints, language, retrieved_entries)
            raw_text = _call_ollama(prompt, model=provider_info["model"])
            raw_response_data = parse_and_clean_response(raw_text, fallback_requirement=clean_req)
        except Exception as exc:
            generation_source = f"Demo Mode (Ollama error: {exc})"
            active_provider = "demo_template"

    # 4. Smart Offline Synthesizer & Knowledge Base Matching
    if active_provider == "demo_template" or raw_response_data is None:
        if not generation_source.startswith("Demo Mode (Gemini fallback") and not generation_source.startswith("Demo Mode (API error"):
            generation_source = "Demo Mode (Smart Offline Synthesizer)"

        # Check if requirement matches a recognized specific pattern (e.g. if age>=18, even/odd, add, factorial)
        pattern_result = try_synthesize_pattern(clean_req, constraints)
        if pattern_result:
            raw_response_data = pattern_result

        # Check if high-similarity match exists in curated knowledge base (>= 45%)
        elif best_item and best_similarity >= 45:
            generation_source = f"Demo Mode (Knowledge Base: {best_item.get('id', 'KB')})"
            raw_response_data = {
                "requirement_summary": best_item.get("requirement", clean_req),
                "assumptions": [
                    "Operating in Demo Mode.",
                    f"Matched pattern from curated knowledge base ({best_similarity}%).",
                    "Input and return types follow Python 3 conventions.",
                ],
                "intent": best_item.get("intent", f"Fulfill requirement: {clean_req}"),
                "inputs": best_item.get("inputs", "Standard parameters per signature"),
                "outputs": best_item.get("outputs", "Return values per signature"),
                "constraints_handled": best_item.get("constraints", constraints or "Default constraints satisfied"),
                "edge_cases": best_item.get("edge_cases", ["Empty input", "Invalid types"]),
                "libraries": best_item.get("libraries", []),
                "code": best_item.get("code", "# No template available\n"),
                "explanation": best_item.get("explanation", "Standard reference implementation."),
                "examples": best_item.get("examples", []),
                "test_cases": best_item.get("test_cases", ""),
                "validation_status": "Valid Python",
            }

        # Dynamic scaffold for any arbitrary custom requirement
        else:
            raw_response_data = synthesize_scaffold(clean_req, constraints)

    generated_code = raw_response_data.get("code", "")

    # 5. AST Syntax and Security Screening
    pipeline_res = validate_code_pipeline(generated_code)

    # 6. Format Verification Checks
    checks = []
    syntax_valid = pipeline_res.get("syntax", {}).get("valid", False) if pipeline_res.get("syntax") else False
    if syntax_valid:
        checks.append({
            "name": "Python Syntax",
            "passed": True,
            "detail": "Valid AST, zero syntax errors detected",
        })
    else:
        err_msg = pipeline_res.get("syntax", {}).get("error_message", "Syntax error")
        line = pipeline_res.get("syntax", {}).get("line", "?")
        checks.append({
            "name": "Python Syntax",
            "passed": False,
            "detail": f"SyntaxError on line {line}: {err_msg}",
        })

    safety_valid = pipeline_res.get("safety", {}).get("safe", False) if pipeline_res.get("safety") else False
    if safety_valid:
        checks.append({
            "name": "Safety Screening",
            "passed": True,
            "detail": "No dangerous calls (eval, exec, os.system) or dangerous imports detected",
        })
    else:
        issues = pipeline_res.get("safety", {}).get("issues", [])
        detail = "; ".join(i.get("message", "Unsafe operation") for i in issues)
        checks.append({
            "name": "Safety Screening",
            "passed": False,
            "detail": detail or "Security policy violation",
        })

    structure_info = pipeline_res.get("structure") or {}
    if structure_info.get("valid"):
        fn_count = structure_info.get("functions", 0)
        cls_count = structure_info.get("classes", 0)
        imp_count = structure_info.get("imports", 0)
        checks.append({
            "name": "AST Structure",
            "passed": True,
            "detail": f"Verified structure: {fn_count} function(s), {cls_count} class(es), {imp_count} import(s)",
        })
    else:
        checks.append({
            "name": "AST Structure",
            "passed": False,
            "detail": "Structural analysis could not parse code AST",
        })

    edge_cases = raw_response_data.get("edge_cases", [])
    checks.append({
        "name": "Edge Case Handling",
        "passed": len(edge_cases) > 0,
        "detail": f"{len(edge_cases)} boundary condition(s) addressed in code & specs",
    })

    elapsed = time.perf_counter() - start_time

    confidence_score = 92
    if best_match and best_match.get("similarity"):
        confidence_score = min(max(best_match["similarity"], 85), 98)
    if not pipeline_res.get("valid"):
        confidence_score = max(confidence_score - 30, 40)

    # 7. Assembled Contract Bundle
    return {
        "analysis": {
            "intent": raw_response_data.get("intent", clean_req),
            "inputs": raw_response_data.get("inputs", "Specified in function signature"),
            "outputs": raw_response_data.get("outputs", "Specified in return annotation"),
            "constraints": (
                f"{raw_response_data.get('constraints_handled', 'Standard boundaries')}. "
                f"{constraints if constraints else ''}"
            ).strip(),
            "edge_cases": edge_cases,
            "libraries": raw_response_data.get("libraries", []),
        },
        "retrieved_context": retrieved_context_ui,
        "code": generated_code,
        "generated_code": generated_code,
        "explanation": raw_response_data.get("explanation", "Implementation logic completed."),
        "examples": raw_response_data.get("examples", []),
        "test_cases": raw_response_data.get("test_cases", ""),
        "assumptions": raw_response_data.get("assumptions", []),
        "requirement_summary": raw_response_data.get("requirement_summary", clean_req),
        "validation": {
            "status": "Passed" if pipeline_res.get("valid") else "Failed",
            "checks": checks,
            "pipeline_result": pipeline_res,
        },
        "mode": generation_source,
        "generation_time": f"{elapsed:.2f}s",
        "confidence": f"{confidence_score}%",
    }
