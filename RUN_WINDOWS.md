# Run Guide (Windows)

This guide covers first-time setup, normal daily start, offline-focused start, and clean shutdown.

Scope of this guide:
- This guide is for the `web-assistant` stack on Windows.
- It covers Flask, PHP/XAMPP, MySQL, and local Ollama-backed assistant services.
- It is not the Raspberry Pi hardware deployment guide for `be-more-agent-main/`.

## Prerequisites

- Python 3.10 or 3.11
- MySQL (or XAMPP MySQL)
- Optional: XAMPP Apache for PHP frontend hosting
- Ollama for local/offline AI inference

## One-Time Setup (New Device)

From project root:

  copy .env.example .env
  copy web-assistant\.env.example web-assistant\.env
  start_all_services.bat

What this does:
- Creates or reuses `.venv`
- Installs a compatible Python version if needed
- Installs pinned Python dependencies
- Starts auth, AI, and web-assistant services

Before first real login, also run:

  .venv\Scripts\python web-assistant\services\auth\setup_users_db.py

And make sure `ollama` is installed, running, and has the required models:

  ollama pull gemma3:1b
  ollama pull moondream

## Daily Start (Recommended)

From project root:

  start_all_services.bat --skip-install

This starts:
- Auth server on port 7000
- AI server on port 8000
- Web assistant backend on port 5000
- PHP frontend on port 8080 (if Apache is serving the PHP frontend)

Health checks:
- http://localhost:7000/health
- http://localhost:8000/health
- http://localhost:5000/health

Frontend:
- http://localhost:8080/loginPage.php
- Or your XAMPP Apache URL if hosted via htdocs

## Offline-Focused Start

Use this after you already installed requirements at least once.

  start_all_services.bat --skip-install

Notes:
- Local AI still requires Ollama running locally.
- No cloud API is required for core chat/inference.
- Any web search feature in the robot needs internet when invoked.

## XAMPP Mode

If XAMPP is installed at C:\xampp (or env var XAMPP_HOME/XAMPP_DIR is set), start MySQL/Apache from the XAMPP control panel before launching the backend.

## Optional Start Flags

- `start_all_services.bat --skip-install`
- `start_all_services.bat --force-reinstall`
- `start_all_services.bat --start-local-pi-web`
- `start_all_services.bat --start-local-pi-agent`
- `start_all_services.bat --start-pi-remote`

## Clean Shutdown

Default stop:

- stop_all_services.bat

Optional:

- `stop_all_services.bat --stop-pi-remote`

## Quick Troubleshooting

1. DB setup fails
- Confirm MySQL is running
- Verify credentials in .env and web-assistant/.env
- Re-run:

  .venv\Scripts\python web-assistant\services\auth\setup_users_db.py

2. Port already in use
- Stop existing process bound to the port, then restart backend:

  stop_all_services.bat
  start_all_services.bat --skip-install

3. Frontend not loading
- If using XAMPP, ensure Apache is running
- If not using Apache, run a local PHP server in `web-assistant/frontend/php`

4. AI not responding
- Ensure Ollama is installed and running
- Confirm model availability with:

  ollama list

5. Python install issues
- Use Python 3.10 or 3.11, not 3.13.
- Let `start_all_services.bat` install Python 3.11 with `winget` if needed.

## Test Checklist

1. Run `start_all_services.bat --skip-install`.
2. Verify all health endpoints respond:
  - `http://localhost:7000/health`
  - `http://localhost:8000/health`
  - `http://localhost:5000/health`
3. Open the frontend and confirm login page loads.
4. Log in and test a basic chat request.
5. If using Pi integration, confirm the Pi Voice Console page still behaves correctly when `PI_WEB_URL` is unreachable.
6. Run `stop_all_services.bat`.

## Suggested Routine

Morning start:
- start_all_services.bat --skip-install

End of day stop:
- stop_all_services.bat
