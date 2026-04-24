#!/bin/bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEMD_DIR="$BASE_DIR/systemd"
USER_NAME="${SUDO_USER:-$USER}"
HOME_DIR="$(getent passwd "$USER_NAME" | cut -d: -f6)"
TARGET_DIR="$HOME_DIR/Ai-Robot/be-more-agent-main"

if [[ ! -d "$TARGET_DIR" ]]; then
  TARGET_DIR="$BASE_DIR"
fi

echo "Installing systemd units for Pi robot autostart..."

sed "s|/home/pi/Ai-Robot/be-more-agent-main|$TARGET_DIR|g; s|User=pi|User=$USER_NAME|g" \
  "$SYSTEMD_DIR/be-more-agent.service" | sudo tee /etc/systemd/system/be-more-agent.service >/dev/null

sed "s|/home/pi/Ai-Robot/be-more-agent-main|$TARGET_DIR|g; s|User=pi|User=$USER_NAME|g" \
  "$SYSTEMD_DIR/be-more-agent-web.service" | sudo tee /etc/systemd/system/be-more-agent-web.service >/dev/null

sudo systemctl daemon-reload
sudo systemctl enable be-more-agent.service
sudo systemctl enable be-more-agent-web.service

echo "Installed. Start now with:"
echo "  sudo systemctl start be-more-agent.service"
echo "  sudo systemctl start be-more-agent-web.service"
echo
echo "Check status with:"
echo "  systemctl status be-more-agent.service"
echo "  systemctl status be-more-agent-web.service"
