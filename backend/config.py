"""
backend/config.py
Lightweight standard library .env loader and configuration manager.
Automatically discovers and loads API keys from .env files without external dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional


def load_env_file(file_path: Optional[str | Path] = None) -> Dict[str, str]:
    """Find and load environment variables from .env file into os.environ.

    Searches current working directory, project root, and parent directories.
    Suppressed during automated testing if CODEFORGE_TEST_MODE=1.
    """
    if os.environ.get("CODEFORGE_TEST_MODE") == "1":
        return {}

    candidates = []
    if file_path:
        candidates.append(Path(file_path))
    else:
        root = Path(__file__).resolve().parent.parent
        candidates.extend([
            Path.cwd() / ".env",
            root / ".env",
            root / "TCS Hackthon" / ".env",
        ])

    loaded = {}
    for p in candidates:
        if p.is_file():
            try:
                with p.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and (k not in os.environ or not os.environ[k]):
                            os.environ[k] = v
                            loaded[k] = v
            except Exception:
                pass
            break  # Stop at first valid .env found

    return loaded


# Automatically load on module import
load_env_file()
