#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[SETUP] Starting Raspberry Pi setup in: $SCRIPT_DIR"

sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip \
  portaudio19-dev espeak git curl wget cmake build-essential libatlas-base-dev

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements_pi.txt

mkdir -p models
mkdir -p whisper.cpp/models
mkdir -p piper
mkdir -p sounds/greeting_sounds sounds/ack_sounds sounds/thinking_sounds sounds/error_sounds
mkdir -p faces/idle faces/listening faces/thinking faces/speaking faces/error faces/capturing faces/warmup

if [ ! -f "models/wakeword.onnx" ]; then
  echo "[WARN] models/wakeword.onnx is missing. Place your wake word model there."
fi

if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git whisper.cpp
fi

if [ ! -x "whisper.cpp/build/bin/whisper-cli" ]; then
  cmake -S whisper.cpp -B whisper.cpp/build
  cmake --build whisper.cpp/build -j"$(nproc)"
fi

if [ ! -f "whisper.cpp/models/ggml-base.en.bin" ]; then
  echo "[SETUP] Downloading Whisper base English model..."
  curl -fL "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin" -o "whisper.cpp/models/ggml-base.en.bin"
fi

ARCH="$(uname -m)"
PIPER_TGZ=""
if [ "$ARCH" = "aarch64" ]; then
  PIPER_TGZ="piper_linux_aarch64.tar.gz"
elif [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "armv6l" ]; then
  PIPER_TGZ="piper_linux_armv7l.tar.gz"
fi

if [ ! -x "piper/piper" ] && [ -n "$PIPER_TGZ" ]; then
  echo "[SETUP] Downloading Piper for $ARCH..."
  TMP_DIR="$(mktemp -d)"
  if curl -fL "https://github.com/rhasspy/piper/releases/download/v1.2.0/${PIPER_TGZ}" -o "${TMP_DIR}/piper.tgz"; then
    tar -xzf "${TMP_DIR}/piper.tgz" -C "$TMP_DIR"
    if [ -f "${TMP_DIR}/piper/piper" ]; then
      cp "${TMP_DIR}/piper/piper" piper/piper
      chmod +x piper/piper
    elif [ -f "${TMP_DIR}/piper" ]; then
      cp "${TMP_DIR}/piper" piper/piper
      chmod +x piper/piper
    fi
  else
    echo "[WARN] Piper binary download failed. Install manually into piper/piper"
  fi
  rm -rf "$TMP_DIR"
fi

if [ ! -f "piper/en_GB-semaine-medium.onnx" ]; then
  echo "[SETUP] Downloading default Piper voice model..."
  if ! curl -fL "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/semaine/medium/en_GB-semaine-medium.onnx" -o "piper/en_GB-semaine-medium.onnx"; then
    echo "[WARN] Voice model download failed. Place one at piper/en_GB-semaine-medium.onnx"
  fi
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "[WARN] Ollama is not installed. Install from https://ollama.com then run:"
  echo "       ollama pull gemma:2b"
  echo "       ollama pull moondream"
else
  ollama pull gemma:2b || true
  ollama pull moondream || true
fi

echo "[SETUP] Done. Next steps:"
echo "1) source .venv/bin/activate"
echo "2) Ensure models/wakeword.onnx exists"
echo "3) python agent.py"
