---
description: Edit a video in Skit (style-06) — funny skit / lip-sync meme: your take timed to a trending sound, close-up ping-pong, emoji reactions
argument-hint: "<path to your take> <path to the sound or the reference reel link> [notes]"
---
Edit this video with the **reel-edit** skill in style **Skit** (`style-06`, no motion page, `scripts/skit_sync.py`): $ARGUMENTS

Follow `/editing-style:edit`, but the video style is already chosen (Skit). Ask in ONE dialog only what's missing:
the reference reel (link, to view and map its cuts; never download it), the sound file, output (Edits app / local render),
and whether you'll post with the platform's original audio (then the sound must stay uncut from 0:00). Then follow
SKILL.md "style-06 Skit": map the ref → anchors (words, beats, hand hits) → `skit_sync.py plan skit.json` → assemble →
title + emoji reactions → export → `finish-export.sh`. Finish with the file path and an honest SHIP / FIX FIRST verdict
(payoff line lips within ±0.1 s, beat hits within ±0.05 s, no speed < 0.7 on movement).
