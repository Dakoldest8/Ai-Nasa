# Web Assistant

This folder contains the active desktop/web assistant stack for the Astronaut AI Ecosystem.

It includes the Python Flask backend and the PHP frontend used by the Windows/XAMPP flow.

## What this component is
- Python Flask backend in [app.py](app.py)
- Central AI routing service in [services/central_server](services/central_server)
- Context-aware recommendation engine with user opt-out in [services/recommendation](services/recommendation)
- Thorium Web EPUB reader integrated in [frontend/epub-reader](frontend/epub-reader) (runs on port 3000) with activity logging for AI learning
- Production deployment monitoring in [services/production_deployment](services/production_deployment)
- Authentication, database, and analytics services in `services/`
- PHP frontend under [frontend/php](frontend/php)

## Recommended setup files
- [../RUN_WINDOWS.md](../RUN_WINDOWS.md) — Windows setup instructions
- [../docs/MYSQL_SETUP.md](../docs/MYSQL_SETUP.md) — MySQL configuration guide
- [../requirements_web_assistant.txt](../requirements_web_assistant.txt) — web assistant Python dependencies
- [../README.md](../README.md) — repository overview

## Main runtime ports
- `5000` — web assistant Flask app
- `8000` — central AI server
- `3000` — Thorium Web EPUB reader
- `8080` or `80` — optional PHP frontend via XAMPP/Apache

## Setup instructions
1. Copy environment templates:
   ```powershell
   copy ..\.env.example ..\.env
   copy .env.example .env
   ```
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements_web_assistant.txt
   ```
3. Configure MySQL credentials in `.env`.
4. Start the backend:
   ```powershell
   python app.py
   ```
5. (Optional) Start the EPUB reader:
   ```powershell
   cd frontend/epub-reader
   pnpm dev
   ```
6. (Optional) To enable reading activity logging, modify `frontend/epub-reader/src/components/Reader.tsx` (or equivalent) to send logs to the AI server:
   ```javascript
   // On book open
   fetch('http://localhost:8000/log_reading', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       user_id: getCurrentUserId(), // Implement user auth
       book_title: bookTitle,
       start_time: new Date().toISOString()
     })
   });

   // On book close
   fetch('http://localhost:8000/log_reading', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       user_id: getCurrentUserId(),
       book_title: bookTitle,
       duration_minutes: Math.round((Date.now() - startTime) / 60000),
       end_time: new Date().toISOString(),
       progress_percent: progress
     })
   });
   ```

If you want the full Windows workflow, run the root `start_all_services.bat` script from the repository root.

## Important notes
- The web assistant uses MySQL as its primary database.
- PHP/XAMPP is only required if you want the PHP web frontend served through Apache.
- The Python backend services run independently of XAMPP.
- The frontend includes a local opt-out toggle for personalized recommendation hints, preserving privacy and user control.
- The integrated Thorium Web EPUB reader is licensed under BSD 3-Clause (see frontend/epub-reader/LICENSE) and is used with permission from Readium Foundation.
- Reading activities are logged to the database for personalized recommendations (book preferences, reading times, stress relief patterns).
- Pi integration is optional: the web assistant can run without the Pi robot present.

## Optional Pi integration
- The web assistant includes Pi integration hooks, but the Pi robot is a separate deployment in `be-more-agent-main/`.
- `PI_WEB_URL` can be set in `.env` to point to a reachable Pi web UI for the voice console.
- If no Pi is available, the web assistant still works locally.

## Current system scope
- The `web-assistant` stack is the active Windows/web target.
- `be-more-agent-main/` is the active Raspberry Pi target.
- `pi-robot/` is deprecated and should no longer be used.
- `be-more-hailo-main/` is reference-only for Hailo hardware.

## Notes on project phases
- The repository currently contains implementation for phases 1 through 8.
- Phase 9 is optional local network sync and is not implemented as a dedicated sync feature yet.
- Production deployment features such as monitoring, auto-scaling, and backup are available under `services/production_deployment`.

## Quick Troubleshooting

- If login fails, verify MySQL is running and rerun `web-assistant/services/auth/setup_users_db.py`.
- If chat fails, verify Ollama is running and `ollama list` shows the required models.
- If the Pi voice page shows offline, that is allowed. Set `PI_WEB_URL` only when the Pi web node is reachable.
