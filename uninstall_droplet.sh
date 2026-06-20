#!/bin/zsh
set -euo pipefail

APP_NAME="Convert Audio to MP3"
INSTALL_SCRIPT="$HOME/.local/bin/mp3-convert"
INSTALL_APP="$HOME/Applications/$APP_NAME.app"

rm -f "$INSTALL_SCRIPT"
rm -rf "$INSTALL_APP"

echo "Removed CLI: $INSTALL_SCRIPT"
echo "Removed droplet: $INSTALL_APP"
