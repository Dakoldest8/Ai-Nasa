# Contributing

## Version Control

1. Create a feature branch for non-trivial changes.
2. Keep commits small and focused.
3. Use short commit titles that describe the change.
4. Add a short body only when the reason is not obvious.

Example:

```text
Fix: keep Pi console optional

- show fallback when Pi is offline
- keep web assistant usable without Pi
```

## Comment Style

1. Keep comments short.
2. Explain why or constraints, not obvious syntax.
3. Update comments when behavior changes.

Good examples:

```python
# Keep this optional so offline mode still works.
# Recreate the venv if Python version is incompatible.
```

## Before You Push

1. Run the affected startup flow.
2. Test the main health endpoints or UI page you changed.
3. Check `git status` for unintended files.
4. Commit with a short message.
5. Push your branch or `main`, depending on the task.

## Minimum Testing Expectations

### Windows / Web Assistant

1. Run `start_all_services.bat --skip-install`.
2. Verify:
   - `http://localhost:7000/health`
   - `http://localhost:8000/health`
   - `http://localhost:5000/health`
3. Open the PHP frontend and confirm login/chat load.
4. Run `stop_all_services.bat`.

### Raspberry Pi Robot

1. Run `bash setup.sh` after dependency changes.
2. Start `bash start_agent.sh` or `bash start_web.sh`.
3. Verify Ollama model availability with `ollama list`.
4. Verify Whisper.cpp files exist:
   - `whisper.cpp/build/bin/whisper-cli`
   - `whisper.cpp/models/ggml-base.en.bin`

### Cross-Component Optional Integration

1. Confirm each component still runs independently offline.
2. If testing the Pi console link, set `PI_WEB_URL` correctly.
3. Verify the web assistant still behaves correctly when the Pi is unreachable.