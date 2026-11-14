#!/bin/zsh
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# 2x full-page screenshot of a public page: screenshot.sh URL OUT.png [height=9000]
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
P=$(mktemp -d "${TMPDIR:-/tmp}/chromeprof.XXXX")
"$C" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$P" --force-device-scale-factor=2 \
  --window-size=1440,${3:-9000} --virtual-time-budget=15000 --screenshot="$2" "$1" >/dev/null 2>&1
sips -g pixelWidth -g pixelHeight "$2" | tail -2
# Find regions: ffmpeg -i OUT.png -vf scale=360:-1 small.png, view it in parts, then crop with assets.py crop (x4 for 2x).
