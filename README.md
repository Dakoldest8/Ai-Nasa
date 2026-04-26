# 🚀 Astronaut AI Ecosystem

A unified AI ecosystem that combines a privacy-first personal assistant with a Raspberry Pi robot companion.

## Current status
- Phases 1 through 8 are implemented in this repository.
- Phase 9 (`Local Network Sync`) is optional and not implemented as a separate dedicated sync service yet.
- Production deployment monitoring, auto-scaling, and backup utilities are available under `web-assistant/services/production_deployment`.
- See `TODO.md` for the current phase progress checklist.

## Active project targets
1. `web-assistant/` — Windows/Desktop web assistant stack
2. `be-more-agent-main/` — Raspberry Pi robot stack
3. `shared/` — shared utilities and datasets

## Important notes
- `pi-robot/` is deprecated and should not be used.
- `be-more-hailo-main/` is reference-only for Hailo hardware.
- `requirements.txt` is for full development only.
- `requirements_web_assistant.txt` is for the web assistant only.
- `be-more-agent-main/requirements.txt` is for the Pi robot only.

## Recommended project files
- `README.md` — this project overview
- `TODO.md` — current phase checklist
- `RUN_WINDOWS.md` — Windows/XAMPP setup for `web-assistant`
- `docs/MYSQL_SETUP.md` — MySQL configuration guide
- `web-assistant/README.md` — web assistant-specific documentation
- `be-more-agent-main/README.md` — Raspberry Pi robot documentation

## Folder overview
```
Astronaut-AI-Ecosystem/
├── web-assistant/           # Active Windows + web assistant stack
├── be-more-agent-main/      # Active Raspberry Pi robot stack
├── shared/                  # Shared utilities, datasets, and helpers
├── docs/                    # Architecture and setup documentation
├── pi-robot/                # Deprecated folder (do not use)
├── be-more-hailo-main/      # Reference-only Hailo fork
├── requirements.txt         # Full ecosystem dependencies
├── requirements_web_assistant.txt  # Web assistant dependencies
├── TODO.md                  # Current phase checklist
├── start_all_services.bat   # Windows service startup wrapper
├── stop_all_services.bat    # Windows service stop wrapper
└── README.md                # This overview
```

## What this system does
- Provides a personal assistant web stack with a Python Flask backend and PHP frontend
- Includes local recommendation hints in the web assistant UI, with a manual opt-out toggle for privacy-preserving behavior
- Integrates Thorium Web EPUB reader for e-book support with activity logging for AI personalization
- Supports AI routing, memory, federated learning, analytics, and robot integration
- Includes a Raspberry Pi robot agent with voice, wake-word, and local LLM capabilities
- Uses local-first AI where possible and avoids cloud dependency for core behavior
- Provides development-friendly modular services for each phase of the system

## Quick start

### Web assistant (Windows/Linux)
```powershell
copy .env.example .env
copy web-assistant\.env.example web-assistant\.env
cd web-assistant
python -m pip install -r requirements_web_assistant.txt
python app.py
```

### Raspberry Pi robot
```bash
cd be-more-agent-main
chmod +x setup.sh start_agent.sh start_web.sh
./setup.sh
./start_agent.sh
# or
./start_web.sh
```

### Full Windows development environment
```powershell
python -m pip install -r requirements.txt
start_all_services.bat
```

## Requirements files
- `requirements.txt` — complete development install for whole repository
- `requirements_web_assistant.txt` — web assistant dependencies only
- `be-more-agent-main/requirements.txt` — Raspberry Pi robot dependencies only

## Architecture notes
- `web-assistant/` is the active web stack.
- `be-more-agent-main/` is the active Pi robot stack.
- `pi-robot/` is deprecated and should no longer be used.
- `be-more-hailo-main/` is reference-only for Hailo hardware.

## Important ports
- `web-assistant` app: `5000`
- `web-assistant` AI server: `8000`
- PHP frontend via XAMPP/Apache: `80`/`8080`
- Thorium Web EPUB reader: `3000`
- Pi robot FastAPI web UI: `8090`

## Running the system
### Web assistant only
```powershell
cd web-assistant
python app.py
```

### Pi robot only
```bash
cd be-more-agent-main
python agent.py
```

### Full web + local assistant experience
```powershell
start_all_services.bat
```

## Notes
- `web-assistant` is the current Windows/web active target.
- `be-more-agent-main` is the current Raspberry Pi target.
- The Pi robot stack is separate from the web assistant stack.
- Production monitoring and backups are implemented in `web-assistant/services/production_deployment`.

cd web-assistant
# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# Run Python backend
python app.py
```

#### 4. Pi Robot
```bash
cd be-more-agent-main

# Install system dependencies (Raspberry Pi only)
# sudo apt-get install portaudio19-dev espeak

# Run robot agent
python agent.py
```

This Pi robot setup is separate from the web assistant setup above. It is hardware-oriented and meant for Raspberry Pi deployment, even though a limited desktop demo mode exists for testing.

---

## 🚀 Running the Ecosystem

### Option 1: Individual Services
```bash
# Terminal 1: Web Assistant Backend
cd web-assistant
python app.py

# Terminal 2: Pi Robot
cd be-more-agent-main
python agent.py

# Terminal 3: Web Frontend (if needed)
cd web-assistant/frontend
php -S localhost:8000
```

This is an offline-first split architecture:
- The Pi robot starts and runs locally on the Raspberry Pi.
- The web assistant starts and runs locally on the Windows/web machine.
- In the PHP chat frontend, users can disable personalized recommendations and keep suggestions local to the browser.
- The EPUB reader can be started separately for e-book reading support.
- Any communication between them is optional and only used when a local mission network exists.
- If the network link is unavailable, both sides continue operating independently.

### Option 2: Using VS Code Tasks
Open Command Palette (`Ctrl+Shift+P`) and select:
- `Tasks: Run Task` → `Start All Services`
- `Tasks: Run Task` → `Start Web Assistant`
- `Tasks: Run Task` → `Start Pi Robot`

---

## 📦 Dependencies

### Python Packages (All Combined in `requirements.txt`)

**Web Assistant Backend:**
- Flask (web framework)
- TensorFlow/PyTorch (federated learning)
- numpy, pandas (data processing)
- python-dotenv (environment management)

**Pi Robot:**
- pyttsx3 (text-to-speech)
- SpeechRecognition (speech-to-text)
- requests (HTTP communication)
- python-dotenv
- Local LLM support (Ollama, Transformers, etc.)

See [requirements.txt](./requirements.txt) for complete list with versions.

---

## 🏗️ Architecture

### Data Flow
```
Astronaut
    ↓
Personal Web App (encrypted, federated learning)
    ↓
Pi Robot (shared knowledge base)
    ↓
Speaks/Interacts with Astronaut
```

### Key Principles
1. **Privacy First**: Personal data never leaves the user's device
2. **Federated Learning**: AI learns from private data without centralizing it
3. **Data Isolation**: Personal vs. Shared data strictly separated
4. **Offline Capability**: Both systems can operate independently

---

### 🏗️ Configuration

### Environment Variables
Create `.env` files in `web-assistant/`.

```env
# Web Assistant - MySQL Connection
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=nasa_ai_system
DB_TABLE=users

# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database URL (SQLAlchemy format)
DATABASE_URL=mysql+pymysql://root:your-mysql-password@localhost:3306/nasa_ai_system

# Pi Robot runtime settings are stored in:
# be-more-agent-main/config.json
```

---

## 🧪 Testing

```bash
# Run tests for web assistant
cd web-assistant
pytest tests/

# Run Pi robot desktop smoke test
cd be-more-agent-main
python agent.py --desktop-test
```

Practical test flow for the current project:

### Windows / Web Assistant
1. Run `start_all_services.bat --skip-install` from the repo root.
2. Check:
    - `http://localhost:7000/health`
    - `http://localhost:8000/health`
    - `http://localhost:5000/health`
3. Open the PHP frontend and confirm login and chat load.
4. Run `stop_all_services.bat`.

### Raspberry Pi Robot
1. Run `bash be-more-agent-main/setup.sh` after dependency changes.
2. Run `bash be-more-agent-main/start_agent.sh` for the robot UI.
3. Run `bash be-more-agent-main/start_web.sh` for the Pi web UI.
4. Confirm `ollama list` shows `gemma3:1b` and `moondream`.
5. Confirm Whisper.cpp files exist under `be-more-agent-main/whisper.cpp/`.

### Offline-First Check
1. Start the Windows stack by itself and verify it still works.
2. Start the Pi by itself and verify it still works.
3. If you test the optional link, set `PI_WEB_URL` and verify the web assistant still degrades gracefully when the Pi is unreachable.

---

## 📚 Documentation

- [Windows Run Guide](./RUN_WINDOWS.md)
- [MySQL Setup Guide](./docs/MYSQL_SETUP.md)
- [Pi Robot README](./be-more-agent-main/README.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Architecture Overview](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Project Structure](./docs/STRUCTURE.md)

---

## 🤝 Contributing
Use [CONTRIBUTING.md](./CONTRIBUTING.md) for version-control rules, comment style, and the standard testing checklist.

---

## 📄 License

[Add your license here]

---

## 🆘 Troubleshooting

### Pi Robot can't connect to Web Assistant
- This link is optional. The Pi robot and web assistant are designed to keep working independently when disconnected.
- If you do want them connected, check firewall settings and verify the target host/port on your local mission network.
- For the web-side Pi console, set `PI_WEB_URL` in `web-assistant/.env` to the Pi web UI address when that node is reachable.

### Windows stack will not start
- Use Python 3.10 or 3.11. Python 3.13 is not supported by the pinned dependency set.
- Run `start_all_services.bat` from the repo root.
- If the first run fails, rerun after `winget` installs Python 3.11.

### Pi speech-to-text is failing
- Run `bash be-more-agent-main/setup.sh` again to install Whisper.cpp and the base English model.
- Confirm `be-more-agent-main/whisper.cpp/build/bin/whisper-cli` exists.
- Confirm `be-more-agent-main/whisper.cpp/models/ggml-base.en.bin` exists.

### Ollama is missing or models are missing
- Install Ollama first.
- On Windows, make sure `ollama` is running locally.
- On Pi, rerun `bash be-more-agent-main/setup.sh` or manually run `ollama pull gemma3:1b` and `ollama pull moondream`.

### Env setup is wrong
- Copy `.env.example` to `.env`.
- Copy `web-assistant/.env.example` to `web-assistant/.env`.
- Update MySQL credentials before starting services.

### Personal data syncing issues
- Check federated learning configuration
- Verify encryption keys match
- Review logs in both services

### Audio issues (TTS/STT)
- Install system audio libraries: `sudo apt-get install portaudio19-dev`
- For Raspberry Pi, also: `sudo apt-get install espeak`

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub.

