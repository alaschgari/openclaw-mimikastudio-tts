#!/usr/bin/env python3
"""MimikaStudio TTS – List available voices and speakers.

Usage:
    python3 list_voices.py [engine]

Examples:
    python3 list_voices.py          # All engines
    python3 list_voices.py qwen3    # Qwen3 only
    python3 list_voices.py kokoro   # Kokoro only
"""

import json
import os
import sys

import requests

BASE_URL = os.environ.get("MIMIKA_API_URL", "http://localhost:7693")
TIMEOUT = 10


def _get_json(endpoint: str) -> dict | None:
    """Fetch JSON from backend endpoint, return None on failure."""
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def list_qwen3() -> dict:
    """List Qwen3 preset speakers and uploaded voice samples."""
    speakers = _get_json("/api/qwen3/speakers")
    voices = _get_json("/api/qwen3/voices")
    return {
        "engine": "qwen3",
        "preset_speakers": speakers.get("speaker_info", {}) if speakers else {},
        "clone_voices": [
            {"name": v["name"], "source": v.get("source", "unknown")}
            for v in (voices or {}).get("voices", [])
        ],
    }


def list_kokoro() -> dict:
    """List Kokoro TTS voices."""
    voices = _get_json("/api/kokoro/voices")
    return {
        "engine": "kokoro",
        "voices": voices.get("voices", []) if voices else [],
    }


def list_all(engine_filter: str | None = None) -> dict:
    """List voices, optionally filtered by engine."""
    result = {"engines": []}

    if engine_filter in (None, "qwen3"):
        result["engines"].append(list_qwen3())
    if engine_filter in (None, "kokoro"):
        result["engines"].append(list_kokoro())

    if not result["engines"]:
        result["error"] = f"Unknown engine: {engine_filter}. Use 'qwen3' or 'kokoro'."

    return result


if __name__ == "__main__":
    engine = sys.argv[1].lower() if len(sys.argv) > 1 else None
    result = list_all(engine)
    print(json.dumps(result, indent=2, ensure_ascii=False))
