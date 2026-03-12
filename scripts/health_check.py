#!/usr/bin/env python3
"""MimikaStudio TTS – Health check.

Checks if the MimikaStudio backend is running and which models are available.

Usage:
    python3 health_check.py
"""

import json
import os
import sys

import requests

BASE_URL = os.environ.get("MIMIKA_API_URL", "http://localhost:7693")
TIMEOUT = 5


def health_check() -> dict:
    """Check backend health and model status."""
    result = {
        "backend": "unreachable",
        "url": BASE_URL,
        "models": None,
    }

    # 1. Health endpoint
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        if r.status_code == 200:
            result["backend"] = "ok"
        else:
            result["backend"] = f"error (HTTP {r.status_code})"
            return result
    except requests.ConnectionError:
        result["hint"] = (
            "Backend not running. Start with: "
            "cd ~/mimika-studio && source venv/bin/activate && "
            "./bin/mimikactl up --no-flutter"
        )
        return result

    # 2. Model status
    try:
        r = requests.get(f"{BASE_URL}/api/models/status", timeout=TIMEOUT)
        if r.status_code == 200:
            result["models"] = r.json()
    except Exception:
        result["models"] = "unavailable"

    # 3. System info
    try:
        r = requests.get(f"{BASE_URL}/api/system/info", timeout=TIMEOUT)
        if r.status_code == 200:
            info = r.json()
            result["system"] = {
                "python": info.get("python_version"),
                "device": info.get("device"),
            }
    except Exception:
        pass

    return result


if __name__ == "__main__":
    result = health_check()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["backend"] != "ok":
        sys.exit(1)
