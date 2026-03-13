#!/usr/bin/env python3
"""MimikaStudio TTS – Generate speech from text.

Usage:
    python3 generate_speech.py '<json_config>'

JSON config fields:
    text        (required)  Text to synthesize
    engine      (optional)  "qwen3" (default) or "kokoro"
    speaker     (optional)  Qwen3 preset speaker, default "Ryan"
    voice       (optional)  Kokoro voice ID, default "bf_emma"
    language    (optional)  Language code, default "de"
    speed       (optional)  Speed multiplier, default 1.0
    output_path (optional)  Where to save the WAV file (default: auto)
    style       (optional)  Style instruction for Qwen3 custom mode

Example:
    python3 generate_speech.py '{"text": "Guten Tag, wie geht es dir?"}'
    python3 generate_speech.py '{"text": "Hallo Welt", "engine": "kokoro", "voice": "bf_emma"}'
"""

import json
import os
import shutil
import sys
import time

import requests

BASE_URL = os.environ.get("MIMIKA_API_URL", "http://localhost:7693")
TIMEOUT_GENERATE = 300  # TTS generation can take minutes for long texts
TIMEOUT_DOWNLOAD = 60


def _health_check() -> bool:
    """Quick health check before generation."""
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        return r.status_code == 200
    except requests.ConnectionError:
        return False


def _generate_qwen3(text: str, speaker: str = "Ryan", language: str = "auto",
                    speed: float = 1.0, style: str | None = None,
                    model_size: str = "1.7B", voice_name: str | None = None) -> dict:
    """Generate speech via Qwen3-TTS.
    
    If voice_name is provided, use 'clone' mode. Otherwise use 'custom' mode with speaker.
    """
    mode = "clone" if voice_name else "custom"
    
    payload = {
        "text": text,
        "mode": mode,
        "language": language,
        "speed": speed,
        "model_size": model_size,
        "model_quantization": "bf16",
    }
    
    if mode == "clone":
        payload["voice_name"] = voice_name
    else:
        payload["speaker"] = speaker
        if style:
            payload["instruct"] = style

    r = requests.post(
        f"{BASE_URL}/api/qwen3/generate",
        json=payload,
        timeout=TIMEOUT_GENERATE,
    )
    r.raise_for_status()
    return r.json()


def _generate_kokoro(text: str, voice: str = "bf_emma",
                     speed: float = 1.0) -> dict:
    """Generate speech via Kokoro TTS."""
    payload = {
        "text": text,
        "voice": voice,
        "speed": speed,
    }
    r = requests.post(
        f"{BASE_URL}/api/kokoro/generate",
        json=payload,
        timeout=TIMEOUT_GENERATE,
    )
    r.raise_for_status()
    return r.json()


def _download_audio(audio_url: str, output_path: str) -> str:
    """Download generated audio file from backend with robust buffering."""
    url = f"{BASE_URL}{audio_url}"
    # Use a longer timeout for the download stream
    r = requests.get(url, timeout=(5, TIMEOUT_DOWNLOAD), stream=True)
    r.raise_for_status()

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    try:
        with open(output_path, "wb") as f:
            # Read in chunks to be more robust against network issues
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise e
    return output_path


def generate_speech(config: dict) -> dict:
    """Main entry point: generate speech from config dict."""
    text = config.get("text", "").strip()
    if not text:
        return {"error": "No text provided", "status": "error"}

    engine = config.get("engine", "qwen3").lower()
    speed = float(config.get("speed", 1.0))
    output_path = config.get("output_path")

    # Health check
    if not _health_check():
        return {
            "error": (
                "MimikaStudio backend not reachable at "
                f"{BASE_URL}. Start it with: "
                "cd ~/mimika-studio && source venv/bin/activate && "
                "./bin/mimikactl up --no-flutter"
            ),
            "status": "error",
        }

    start = time.time()

    try:
        if engine == "kokoro":
            voice = config.get("voice", "bf_emma")
            result = _generate_kokoro(text, voice=voice, speed=speed)
        else:
            language = config.get("language", "de")
            
            # Default to 1.7B for German unless specified
            default_model = "1.7B" if language.lower() in ["de", "german"] else "0.6B"
            model_size = config.get("model_size", default_model)
            
            # Extract voice/speaker
            voice = config.get("voice")
            speaker = config.get("speaker", "Ryan")
            
            # If a known Qwen3 preset speaker is used as 'voice', map it to speaker
            QWEN_SPEAKERS = ["Ryan", "Aiden", "Vivian", "Serena", "Uncle_Fu", "Dylan", "Eric", "Ono_Anna", "Sohee"]
            if voice in QWEN_SPEAKERS:
                speaker = voice
                voice = None
            
            # For German 'Max' and 'Natasha' are currently voice prompts (clone mode)
            if language.lower() in ["de", "german"] and not voice:
                voice = "Max" # Default German voice

            style = config.get("style")
            result = _generate_qwen3(
                text, speaker=speaker, language=language,
                speed=speed, style=style,
                model_size=model_size, voice_name=voice
            )

        audio_url = result.get("audio_url")
        filename = result.get("filename", "output.wav")

        if not audio_url:
            return {"error": "No audio_url in response", "status": "error",
                    "raw_response": result}


        # Determine output path
        if not output_path:
            output_dir = os.path.expanduser("~/MimikaStudio/outputs")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, filename)

        _download_audio(audio_url, output_path)
        elapsed = round(time.time() - start, 2)

        return {
            "status": "ok",
            "file": output_path,
            "filename": filename,
            "engine": engine,
            "duration_sec": elapsed,
            "chars": len(text),
        }

    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        detail = ""
        if e.response is not None:
            try:
                detail = e.response.json().get("detail", e.response.text)
            except Exception:
                detail = e.response.text
        return {
            "error": f"HTTP {status_code}: {detail}",
            "status": "error",
            "hint": (
                "If status 409: model not downloaded yet. "
                "Open MimikaStudio UI or run: "
                "./bin/mimikactl models download qwen3"
            ) if status_code == 409 else None,
        }
    except requests.ConnectionError:
        return {"error": "Backend connection lost during generation",
                "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_speech.py '<json_config>'")
        print('Example: python3 generate_speech.py \'{"text": "Hello World"}\'')
        sys.exit(1)

    try:
        config = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}", "status": "error"}))
        sys.exit(1)

    result = generate_speech(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    

    if result.get("status") == "error":
        sys.exit(1)
