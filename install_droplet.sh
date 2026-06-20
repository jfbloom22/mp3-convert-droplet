#!/bin/zsh
set -euo pipefail

APP_NAME="Convert Audio to MP3"
INSTALL_BIN_DIR="$HOME/.local/bin"
INSTALL_APP_DIR="$HOME/Applications"
INSTALL_SCRIPT="$INSTALL_BIN_DIR/mp3-convert"
INSTALL_APP="$INSTALL_APP_DIR/$APP_NAME.app"
SOURCE_DIR="${0:A:h}"
SOURCE_SCRIPT="$SOURCE_DIR/convert_audio_to_mp3.py"

if [[ ! -f "$SOURCE_SCRIPT" ]]; then
  echo "Could not find converter script: $SOURCE_SCRIPT" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1 && [[ ! -x /opt/homebrew/bin/ffmpeg && ! -x /usr/local/bin/ffmpeg ]]; then
  cat >&2 <<'EOF'
ffmpeg was not found.

Install it with Homebrew:
  brew install ffmpeg

Then rerun:
  ./install_droplet.sh
EOF
  exit 1
fi

mkdir -p "$INSTALL_BIN_DIR" "$INSTALL_APP_DIR"
cp "$SOURCE_SCRIPT" "$INSTALL_SCRIPT"
chmod +x "$INSTALL_SCRIPT"

rm -rf "$INSTALL_APP"

osacompile -o "$INSTALL_APP" -e "
on open droppedItems
  set presetOptions to {\"Music - highest quality\", \"Audiobook - voice acting and sound effects\"}
  set presetChoice to choose from list presetOptions with title \"$APP_NAME\" with prompt \"Choose MP3 quality for this batch:\" default items {\"Music - highest quality\"} OK button name \"Convert\" cancel button name \"Cancel\"
  if presetChoice is false then return

  if item 1 of presetChoice is \"Audiobook - voice acting and sound effects\" then
    set presetName to \"audiobook\"
  else
    set presetName to \"music\"
  end if

  set quotedPaths to \"\"
  repeat with droppedItem in droppedItems
    set posixPath to POSIX path of droppedItem
    set quotedPaths to quotedPaths & \" \" & quoted form of posixPath
  end repeat

  set commandText to quoted form of \"$INSTALL_SCRIPT\" & \" --trash-originals --preset \" & presetName & quotedPaths
  try
    do shell script commandText
    display notification \"Audio conversion finished.\" with title \"$APP_NAME\"
  on error errorMessage number errorNumber
    display dialog \"Audio conversion failed:\" & return & return & errorMessage buttons {\"OK\"} default button \"OK\" with icon stop
  end try
end open

on run
  display dialog \"Drop audio files or folders onto this app to convert them to MP3.\" buttons {\"OK\"} default button \"OK\"
end run
"

echo "Installed CLI: $INSTALL_SCRIPT"
echo "Installed droplet: $INSTALL_APP"
echo "Drag the app to the Dock, then drop files or folders onto it."
