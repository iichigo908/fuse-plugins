#!/bin/bash
# Copies the Fusion folder next to this file into DaVinci Resolve's Fusion user folder (Mac).
# Double-click in Finder (first time: right-click > Open). Quit DaVinci Resolve first.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="${PLUGIN_DEST:-$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion}"
echo "Installing to: $DEST"
mkdir -p "$DEST"
cp -R "$HERE/Fusion/." "$DEST/"
echo ""
echo "Done. Start DaVinci Resolve. / 完了しました。DaVinci Resolve を起動してください。"
if [ -z "$PLUGIN_DEST" ]; then read -n 1 -s -r -p "Press any key to close"; echo; fi
