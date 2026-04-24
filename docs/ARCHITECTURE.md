# Architecture

This file describes the current practical structure of the repo, not an aspirational future design.

## Two Main Runtime Targets

### 1. Web Assistant

Runs on a desktop/laptop/server.

Main pieces:

- `web-assistant/app.py`
- `web-assistant/services/auth/auth_server.py`
- `web-assistant/services/central_server/ai_server.py`
- `web-assistant/frontend/php/`

Typical local ports:

- `5000` web-assistant app
- `7000` auth server
- `8000` central AI server

Supporting services:

- MySQL for users/auth and setup schema
- XAMPP/Apache or PHP built-in server for the PHP frontend
- Ollama for local LLM-backed chat

### 2. Pi Robot

Runs on Raspberry Pi hardware.

Main pieces:

- `be-more-agent-main/agent.py`
- `be-more-agent-main/config.json`
- `be-more-agent-main/wakeword.onnx`

Pi-side features:

- wake word
- face animation GUI
- local Ollama inference
- Piper voice output
- Whisper.cpp-based speech input
- optional camera capture

There is also a desktop demo mode for testing the robot UI without full Pi hardware.

## How The Web Assistant Is Structured

### Flask App Layer

`web-assistant/app.py` is the main app entry point.

It exposes:

- app health/status endpoints
- forwarded auth routes
- forwarded AI chat route

### Auth Layer

`web-assistant/services/auth/` contains:

- MySQL auth server
- MySQL setup script
- SQL bootstrap schema

The current schema uses:

- `nasa_ai_system` database
- `users.user_id` as the stable numeric identifier

### Central AI Layer

`web-assistant/services/central_server/` contains:

- memory handling
- topic routing
- local Ollama client
- specialty agent logic

The PHP assistant UI talks to this service on port `8000`.

### PHP Frontend Layer

`web-assistant/frontend/php/` contains the user-facing pages.

Current behavior:

- login is handled through the Python auth server
- chat is handled through the central AI server
- notes and reminders are file-backed per logged-in user in the PHP folder

## Data Separation

The repo separates the two usage patterns intentionally:

### Web Assistant

- user-specific login
- user-specific notes/reminders
- desktop/web workflow

### Pi Robot

- hardware-focused local assistant
- shared/non-personal interaction style
- no XAMPP/PHP dependency

## Current Setup Entry Points

Use these instead of old generic setup flows:

1. `RUN_WINDOWS.md`
- Windows + XAMPP + MySQL + web-assistant

2. `docs/MYSQL_SETUP.md`
- MySQL details and troubleshooting

3. `be-more-agent-main/README.md`
- Pi-specific setup and runtime

## What This File Does Not Try To Do

This file intentionally does not document:

- speculative deployment clusters
- unimplemented JWT/RBAC systems
- unfinished API contracts
- old SQLite-based architecture

Those details were removed to keep the architecture notes aligned with the current repository.
