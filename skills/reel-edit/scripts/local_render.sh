#!/bin/zsh
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# LOCAL render (no Edits app): motion page + face/voice + music + sound effects -> finished video at -14 LUFS.
#   zsh local_render.sh motion.html face-cut.mp4|none OUT.mp4 [music.mp3|none] [music_volume=0.12] [sfx_dir]
# - face-cut.mp4 (from local_cut.py) is drawn inside every .facecard / creator window (render.mjs --face); its audio is
#   the voice. "none" = no recording (text + screenshot videos).
# - music is ducked under the voice (sidechain). Use only music you have the rights to.
# - sfx_dir (default ./reel-library/sfx): sfx_cues.py finds EVERY sound moment on the page (page cuts, popups, pills,
#   typing, highlights, count hits) and mixes whoosh.* popup.* tick.* typing.* highlight.* hit.* from that folder.
# - Aspect: pass W/H through env, e.g. W=3840 H=2160 for 16:9 (default 1440x2560).
set -e
D=${0:A:h}; PAGE="$1"; FACE="$2"; OUT="$3"; MUSIC="${4:-none}"; MV="${5:-0.12}"; SFX="${6:-./reel-library/sfx}"
[ -f "$PAGE" ] || { echo "usage: local_render.sh motion.html face-cut.mp4|none OUT.mp4 [music|none] [vol] [sfx_dir]"; exit 1; }
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
SIZE=(--w "${W:-1440}" --h "${H:-2560}")
if [ "$FACE" != "none" ]; then
  cp "$FACE" "${PAGE:h}/__face.mp4"; node "$D/render.mjs" "$PAGE" "$TMP/video.mp4" "${SIZE[@]}" --face __face.mp4; rm -f "${PAGE:h}/__face.mp4"
else
  node "$D/render.mjs" "$PAGE" "$TMP/video.mp4" "${SIZE[@]}"
fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/video.mp4")
# audio layers (input 0 is the video): voice, music, sfx, each optional
IN=(); F=""; N=1; MIX=""; K=0; VOICE=""
if [ "$FACE" != "none" ] && ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$FACE" | grep -q .; then
  IN+=(-i "$FACE"); F+="[${N}:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit[v][vk];"; VOICE=1; N=$((N+1)); MIX+="[v]"; K=$((K+1)); fi
if [ "$MUSIC" != "none" ] && [ -f "$MUSIC" ]; then
  FO=$(python3 -c "print(max(0,$DUR-1.5))")
  IN+=(-stream_loop -1 -i "$MUSIC"); F+="[${N}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=$MV,afade=t=in:d=0.5,afade=t=out:st=${FO}:d=1.5[m0];"
  if [ -n "$VOICE" ]; then F+="[m0][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[m];"; else F+="[m0]anull[m];"; fi
  N=$((N+1)); MIX+="[m]"; K=$((K+1)); fi
[ -n "$VOICE" ] && [ "$MUSIC" = "none" -o ! -f "$MUSIC" ] && F+="[vk]anullsink;"
if [ -d "$SFX" ]; then python3 -I "$D/sfx_cues.py" "$PAGE" --mix "$SFX" "$TMP/sfx.wav" | tail -2; fi
if [ -f "$TMP/sfx.wav" ]; then IN+=(-i "$TMP/sfx.wav"); F+="[${N}:a]anull[s];"; N=$((N+1)); MIX+="[s]"; K=$((K+1)); fi
if [ $K -eq 0 ]; then cp "$TMP/video.mp4" "$OUT"; echo "no audio layers: wrote silent $OUT"; exit 0; fi
ffmpeg -y -loglevel error -i "$TMP/video.mp4" "${IN[@]}" -filter_complex "${F}${MIX}amix=inputs=${K}:duration=longest:normalize=0,atrim=0:${DUR}[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 320k "$TMP/mux.mp4"
zsh "$D/finish-export.sh" "$TMP/mux.mp4" "$OUT"
