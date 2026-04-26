# Project Structure

This document lists the current high-value files and folders you actually need to care about.

## Authoritative Setup Files

- `README.md`
- `RUN_WINDOWS.md`
- `docs/MYSQL_SETUP.md`
- `be-more-agent-main/README.md`

## Current Top-Level Layout

```
Ai-Robot/
├── requirements_web_assistant.txt # Windows/web-assistant runtime dependencies
├── requirements.txt               # Combined dependency reference
├── README.md                      # Main repo overview and routing guide
├── RUN_WINDOWS.md                 # Windows/XAMPP/MySQL run guide
├── robot_agent.py                 # Optional consolidated Pi runtime variant
├── robot_web_app.py               # Optional consolidated FastAPI interface
├── robot_config.json              # Config for consolidated runtime variant
├── .env.example                   # Root env template
├── docs/
│   ├── MYSQL_SETUP.md             # MySQL/XAMPP setup and troubleshooting
│   ├── ARCHITECTURE.md            # System architecture
│   ├── API.md                     # API notes
│   └── STRUCTURE.md               # This file
├── web-assistant/
│   ├── app.py                     # Flask entry point
│   ├── README.md                  # Web-assistant scope notes
│   ├── .env.example               # Web-assistant env template
│   ├── frontend/php/              # PHP pages for XAMPP/Apache
│   └── services/
│       ├── auth/                  # MySQL auth setup and auth server
│       ├── central_server/        # Main AI chat service
│       ├── federated_learning/    # FL-related code
│       └── devices/               # Device-specific FL clients
├── be-more-agent-main/
│   ├── agent.py                   # Active Pi robot UI + local AI runtime
│   ├── README.md                  # Pi robot setup and runtime instructions
│   ├── config.json                # Pi robot model/settings config
│   └── wakeword.onnx              # Wake word model
├── pi-robot/
│   ├── agent.py                   # Legacy compatibility variant
│   ├── README.md                  # Legacy Pi docs (kept for reference)
│   ├── requirements_pi.txt        # Legacy Pi-specific dependencies
│   ├── config/config.json         # Legacy config layout
│   └── models/wakeword.onnx       # Legacy wake word path
└── shared/
   └── datasets/                  # Shared data helpers
```

## Key Directories Explained

### be-more-agent-main/
- **Autonomous Raspberry Pi agent** with local LLM
- Handles speech recognition, TTS, and shared knowledge access
- Minimal dependencies on external services
- Runs independently in spacecraft

### web-assistant/
- **Privacy-focused web application** with federated learning
- Flask backend with encrypted personal data
- PHP frontend for web interface
- Database for task management and learning

### shared/
- **Common code shared between components**
- API communication utilities
- Data schemas and validation
- Authentication and logging helpers

### docs/
- **Complete documentation** for the project
- Architecture diagrams
- API specifications
- Deployment procedures

## Which Path To Follow

1. Web assistant on Windows/XAMPP:
- Use `README.md` then `RUN_WINDOWS.md`

2. MySQL troubleshooting:
- Use `docs/MYSQL_SETUP.md`

3. Pi hardware robot setup:
- Use `be-more-agent-main/README.md`

## Notes

- Windows setup and startup steps are documented in `RUN_WINDOWS.md`.
- The Pi robot has its own dependency and runtime path and should not be mixed with the XAMPP/PHP setup.
