# OpenClaw MimikaStudio TTS Skill

Ein [OpenClaw](https://github.com/openclaw) Skill zur Sprachgenerierung über das lokale [MimikaStudio](https://github.com/BoltzmannEntropy/MimikaStudio) Backend.

## Voraussetzungen

1. **MimikaStudio** installiert unter `~/mimika-studio`
2. **Backend gestartet:**
   ```bash
   cd ~/mimika-studio && source venv/bin/activate
   ./bin/mimikactl up --no-flutter
   ```
3. **Python 3.10+** mit `requests` installiert

## Schnellstart

```bash
# Health Check
python3 scripts/health_check.py

# Stimmen auflisten
python3 scripts/list_voices.py

# Sprache generieren (Qwen3, Speaker Ryan)
python3 scripts/generate_speech.py '{"text": "Hallo Welt, das ist ein Test."}'

# Mit Kokoro (schneller, nur Englisch)
python3 scripts/generate_speech.py '{"text": "Hello World", "engine": "kokoro"}'
```

## Konfiguration

| Feld | Default | Beschreibung |
|------|---------|-------------|
| `text` | *required* | Text zur Synthese |
| `engine` | `qwen3` | `qwen3` oder `kokoro` |
| `speaker` | `Ryan` | Qwen3 Preset Speaker |
| `voice` | `bf_emma` | Kokoro Voice ID |
| `language` | `auto` | Sprachcode |
| `speed` | `1.0` | Geschwindigkeit (0.5–2.0) |
| `style` | – | Style-Instruktion für Qwen3 |
| `output_path` | auto | Ziel-Pfad für die WAV-Datei |

## Umgebungsvariablen

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `MIMIKA_API_URL` | `http://localhost:7693` | Backend URL |
