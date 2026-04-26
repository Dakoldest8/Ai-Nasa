#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

source venv/bin/activate
exec python -m uvicorn web_app:app --host 0.0.0.0 --port 8090
