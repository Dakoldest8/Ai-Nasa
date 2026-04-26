<!-- Astronaut AI Ecosystem - Workspace Instructions -->

# Astronaut AI Ecosystem Setup

## Project Structure
- **be-more-agent-main/**: Raspberry Pi robot with local LLM, TTS/STT capabilities
- **web-assistant/**: Web-based personal AI with federated learning backend
- **shared/**: Shared utilities, APIs, and common code
- **docs/**: Documentation and architecture guides

## Installation Requirements

### Global Dependencies
- Python 3.9+
- Node.js 18+ (for web frontend tooling)
- PHP 8.0+ (for web backend)
- Git

### Python Dependencies (Combined)
See `requirements.txt` for all Python packages needed for both components.

### Quick Start
1. On Windows, follow `RUN_WINDOWS.md` for the `web-assistant` stack
2. Configure `.env` files with your settings
3. Use `RUN_WINDOWS.md` for desktop/XAMPP/MySQL setup and `be-more-agent-main/README.md` for the Pi robot flow

## Development Workflow
- Both components run independently but can share utilities from `/shared`
- Pi robot communicates via WebSocket/HTTP with web assistant
- Personal data stays federated; shared knowledge remains on Pi
