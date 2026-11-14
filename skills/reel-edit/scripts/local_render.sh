#!/bin/zsh
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# LOCAL render (no Edits app): motion page + face video + audio -> finished reel at -14 LUFS.
#   zsh local_render.sh motion.html face-cut.mp4|none OUT.mp4 [music.mp3] [music_volume=0.12]
# - face-cut.mp4 (from local_cut.py) is drawn inside every .facecard / creator window of the page (render.mjs --face),
#   and its audio is the voice track. Use "none" for a page with no face (then no voice either, unless the page has one).
# - Optional music bed is mixed under the voice with sidechain ducking.
set -e
D=${0:A:h}; PAGE="$1"; FACE="$2"; OUT="$3"; MUSIC="$4"; MV="${5:-0.12}"
[ -f "$PAGE" ] || { echo "usage: local_render.sh motion.html face-cut.mp4|none OUT.mp4 [music.mp3] [vol]"; exit 1; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
if [ "$FACE" != "none" ]; then
  cp "$FACE" "${PAGE:h}/__face.mp4"
  node "$D/render.mjs" "$PAGE" "$TMP/video.mp4" --face __face.mp4
  rm -f "${PAGE:h}/__face.mp4"
else
  node "$D/render.mjs" "$PAGE" "$TMP/video.mp4"
fi
if [ "$FACE" != "none" ] && ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$FACE" | grep -q .; then
  if [ -n "$MUSIC" ]; then
    ffmpeg -y -loglevel error -i "$TMP/video.mp4" -i "$FACE" -stream_loop -1 -i "$MUSIC" -filter_complex \
      "[2:a]volume=$MV[m];[m][1:a]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];[1:a][md]amix=inputs=2:duration=first:normalize=0[a]" \
      -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 320k -shortest "$TMP/mux.mp4"
  else
    ffmpeg -y -loglevel error -i "$TMP/video.mp4" -i "$FACE" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest "$TMP/mux.mp4"
  fi
  zsh "$D/finish-export.sh" "$TMP/mux.mp4" "$OUT"
else
  cp "$TMP/video.mp4" "$OUT"; echo "no audio track: wrote silent $OUT"
fi
