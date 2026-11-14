#!/bin/zsh
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# Final loudness pass for every export.
#   zsh scripts/finish-export.sh IN.mp4 [OUT.mp4]
# Two-pass ffmpeg loudnorm to -14 LUFS integrated, true peak <= -1.5 dBTP, LRA 11. The video stream is copied untouched
# (no re-encode); audio is re-encoded as AAC 320k 48 kHz. Default OUT = IN with "-final" before the extension.
# Prints the measured loudness of IN and OUT, so gate 2 can read the real numbers.
set -e
IN="$1"; OUT="${2:-${IN%.*}-final.${IN##*.}}"
[ -f "$IN" ] || { echo "no such file: $IN"; exit 1; }
J=$(ffmpeg -hide_banner -nostats -i "$IN" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -I -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
echo "in : $(g input_i) LUFS, true peak $(g input_tp) dBTP, LRA $(g input_lra)"
ffmpeg -hide_banner -loglevel error -y -i "$IN" -map 0 -c:v copy -c:a aac -b:a 320k -ar 48000 \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true" \
  -movflags +faststart "$OUT"
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' | grep -E "I:|Peak:" | tr -s ' ' | paste -sd' ' - | sed 's/^/out: /'
echo "$OUT"
