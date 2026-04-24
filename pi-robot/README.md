# ⚠️ Pi Robot - DEPRECATED - DO NOT USE

**THIS FOLDER IS DEPRECATED AND NO LONGER MAINTAINED!**

## Where to go instead:

The Raspberry Pi robot code has been **consolidated into `be-more-agent-main/`**.

Use these resources instead:

1. **Main Robot Setup**: [be-more-agent-main/README.md](../be-more-agent-main/README.md)
2. **Main Repo README**: [README.md](../README.md)
3. **Installation**: `be-more-agent-main/setup.sh`
4. **Quick Start**: `cd be-more-agent-main && bash setup.sh`

## What was here

This folder contained the original Raspberry Pi-based intelligent robot with:
- Local LLM (via Ollama)
- Text-to-Speech (via Piper)
- Speech-to-Text (via Whisper.cpp)
- Wake-word detection (via OpenWakeWord)
- Shared knowledge base access
- Designed for zero-connectivity environments

**All of this functionality now lives in [`be-more-agent-main/`](../be-more-agent-main) with additional features:**
- FastAPI web interface for browser access
- Interactive timers, games, and music
- Camera vision capabilities
- Pronunciation customization
- And more!

## Migration Notes

If you have custom code that referenced `pi-robot/`:
- Update imports to use `be-more-agent-main/` instead
- `config.json` location: `be-more-agent-main/config.json`
- `agent.py` location: `be-more-agent-main/agent.py`
- `web_app.py` location: `be-more-agent-main/web_app.py`

Do not delete this folder yet (for git history), but use `be-more-agent-main/` going forward.

2. `sounds/` effect folders

Without `whisper.cpp`, the mic speech-to-text path will not work.
Without `piper`, spoken audio output will be skipped.
Without `faces/`, the GUI falls back to a plain screen instead of animated character faces.

## Quick Start

### Setup
```bash
# From project root
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements_pi.txt
```

### Raspberry Pi Specific Setup
```bash
# Install system audio libraries
sudo apt-get update
sudo apt-get install -y portaudio19-dev espeak git cmake build-essential libatlas-base-dev

# Install Ollama for local LLM (optional)
# https://ollama.ai
```

### Install Python Dependencies

```bash
pip install -r requirements_pi.txt
```

### One-Command Pi Setup

Use the setup script to install dependencies, build Whisper.cpp, create required folders, and attempt Piper/model downloads:

```bash
cd pi-robot
chmod +x setup_pi.sh
./setup_pi.sh
```

### Install Ollama Models

```bash
ollama serve
ollama pull gemma:2b
ollama pull moondream
```

### Place the Wake Word Model

The current agent now expects the wake word model at:

```bash
pi-robot/models/wakeword.onnx
```

If you train or download a new wake word model, put it there with that filename.

### Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Run
```bash
python agent.py
```

Run this from inside the `pi-robot/` folder.

The wake word path and config path are now resolved relative to `agent.py`, so they no longer depend on the current shell directory.

## Architecture

- **Local LLM**: Ollama/Transformers for offline inference
- **Speech Recognition**: Google Speech-to-Text or offline alternatives
- **Text-to-Speech**: pyttsx3 for audio output
- **Knowledge Base**: Shared, non-personal information accessible to all crew
- **Flask API**: REST endpoints for query processing

## Key Endpoints

- `GET /health` - Health check
- `POST /api/query` - Process user query with LLM
- `POST /api/play-game` - Start interactive game
- `GET /api/tutorials` - List available tutorials
- `GET /api/knowledge` - Query knowledge base

## Features

- ✅ Local LLM inference (no internet required)
- ✅ Speech-to-Text input
- ✅ Text-to-Speech output
- ✅ Shared knowledge base
- ✅ Interactive games
- ✅ Tutorial playback
- ✅ Raspberry Pi touch screen support

## Offline Capability

This robot is designed to operate completely offline:
- No internet connection required
- All models run locally on Raspberry Pi
- Can handle thousands of queries without external services

## Performance

- **Response Time**: < 2 seconds for typical queries (Ollama)
- **Memory Usage**: ~2-4GB (depends on model size)
- **CPU Usage**: ~50-80% during inference

## Development

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
flake8 .
pylint **/*.py
black .
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `ROBOT_NAME`: Display name for the robot
- `LOCAL_LLM`: LLM engine (ollama, transformers, etc.)
- `TTS_ENGINE`: Text-to-speech engine
- `STT_ENGINE`: Speech-to-text engine

## Troubleshooting

### Ollama not responding
- Ensure Ollama is running: `ollama serve`
- Check Ollama host/port in `.env`

### No audio output
- Check audio device index: `python -c "import sounddevice; print(sounddevice.query_devices())"`
- Verify speaker connection (Raspberry Pi)

### High CPU usage
- Use smaller LLM model in Ollama
- Enable caching for repeated queries

### Memory insufficient
- Reduce LLM model size
- Close other applications

## Hardware Requirements

### Minimum
- Raspberry Pi 4 (4GB RAM)
- 16GB microSD card
- USB microphone
- USB speaker or audio output

### Recommended  
- Raspberry Pi 4 (8GB RAM)
- 64GB microSD card / external USB drive
- 7" touch screen display
- USB microphone with button
- Quality audio amplifier

## Installation from Scratch

1. Flash Raspberry Pi OS to microSD card
2. Enable SSH and set up WiFi
3. SSH into Pi and run:
   ```bash
   git clone <repo-url>
   cd Ai-Robot
   python3 -m venv venv
   source venv/bin/activate
   cd pi-robot
   pip install -r requirements_pi.txt
   ```
4. Configure `.env` for your hardware
5. Run `python agent.py`
