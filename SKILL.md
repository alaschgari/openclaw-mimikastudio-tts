| Name | Description | Homepage | Dependencies |
| :--- | :--- | :--- | :--- |
| MimikaStudio TTS | Text-to-Speech via lokales MimikaStudio Backend (Qwen3, Kokoro) | http://localhost:7693/docs | python3, requests |

# MimikaStudio TTS Skill

Dieser Skill ermöglicht OpenClaw, Text in Sprache umzuwandeln. Er ist auf **deutsche Sprachausgabe** optimiert und nutzt das lokal laufende **MimikaStudio Backend** (FastAPI, Port 7693) mit Qwen3-TTS und Kokoro-TTS.

> [!IMPORTANT]
> Das MimikaStudio Backend muss lokal laufen, bevor dieser Skill genutzt werden kann:
> ```bash
> cd ~/mimika-studio && source venv/bin/activate && ./bin/mimikactl up --no-flutter
> ```

## Usage

### Sprache generieren

OpenClaw kann Text in eine WAV-Datei umwandeln:

**Deutsch:**
- „Lies mir diesen Text vor: Hallo Welt, das ist ein Test."
- „Generiere eine Sprachdatei mit dem Text: Die Sonne scheint heute besonders schön."
- „Erstelle eine Audio-Datei mit Ryan als Sprecher: Guten Tag, wie kann ich dir heute helfen?"

**Englisch:**
- "Generate speech: Hello World, this is a test."
- "Read this text aloud with Aiden: The quick brown fox jumps over the lazy dog."

OpenClaw wird:
1. Prüfen, ob das Backend erreichbar ist (`scripts/health_check.py`)
2. Den Text an die TTS-API senden (`scripts/generate_speech.py`)
3. Die generierte WAV-Datei zurückgeben

### Verfügbare Stimmen auflisten

„Welche Stimmen sind verfügbar?" → `scripts/list_voices.py`

### Engines

| Engine | Typ | Default Speaker | Sprachen |
|--------|-----|-----------------|----------|
| **qwen3** (default) | Custom Voice (Preset) | Ryan | de (default), en, zh, ja, ko |
| **kokoro** | Fast TTS | bf_emma | en (British/American) |

### Qwen3 Preset Speakers

| Speaker | Sprache | Charakter |
|---------|---------|-----------|
| Ryan | English | Dynamic male, strong rhythm |
| Aiden | English | Sunny American male |
| Vivian | Chinese | Bright young female |
| Serena | Chinese | Warm gentle female |
| Ono_Anna | Japanese | Playful female |
| Sohee | Korean | Warm emotional female |

### Backend-Status prüfen

„Ist das MimikaStudio Backend erreichbar?" → `scripts/health_check.py`

## Scripts

- `scripts/generate_speech.py`: Text → WAV-Datei generieren (Haupt-Script)
- `scripts/list_voices.py`: Verfügbare Engines, Speakers und Voices auflisten
- `scripts/health_check.py`: Backend-Verfügbarkeit und Modell-Status prüfen

## Beispiel-Aufrufe

```bash
# Sprache generieren (Qwen3, Speaker Ryan, Default Sprache: de)
python3 scripts/generate_speech.py '{"text": "Guten Tag, Welt"}'

# Mit Kokoro Engine
python3 scripts/generate_speech.py '{"text": "Hello World", "engine": "kokoro", "voice": "bf_emma"}'

# Stimmen auflisten
python3 scripts/list_voices.py

# Backend-Status
python3 scripts/health_check.py
```
