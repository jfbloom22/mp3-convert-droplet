#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h}"
RENDERER="$ROOT_DIR/scripts/render_app_icon.py"
ICONSET="$ROOT_DIR/assets/app-icon.iconset"
ICNS="$ROOT_DIR/assets/app-icon.icns"

if [[ ! -f "$RENDERER" ]]; then
  echo "Missing icon renderer: $RENDERER" >&2
  exit 1
fi

rm -rf "$ICONSET"
mkdir -p "$ICONSET"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

base_png="$tmpdir/app-icon.png"
"$RENDERER" --size 1024 --out "$base_png"

sips -s format png -z 16 16 "$base_png" --out "$ICONSET/icon_16x16.png" >/dev/null
sips -s format png -z 32 32 "$base_png" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
sips -s format png -z 32 32 "$base_png" --out "$ICONSET/icon_32x32.png" >/dev/null
sips -s format png -z 64 64 "$base_png" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
sips -s format png -z 128 128 "$base_png" --out "$ICONSET/icon_128x128.png" >/dev/null
sips -s format png -z 256 256 "$base_png" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
sips -s format png -z 256 256 "$base_png" --out "$ICONSET/icon_256x256.png" >/dev/null
sips -s format png -z 512 512 "$base_png" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
sips -s format png -z 512 512 "$base_png" --out "$ICONSET/icon_512x512.png" >/dev/null
sips -s format png -z 1024 1024 "$base_png" --out "$ICONSET/icon_512x512@2x.png" >/dev/null

iconutil -c icns "$ICONSET" -o "$ICNS"
echo "Built icon: $ICNS"
