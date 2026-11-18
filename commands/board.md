---
description: Edit a video in Board (style-07) — 16:9, the footage always on screen as a moving card, real app / site screens with zoom-to-highlight, brand sting and end card
argument-hint: "<path to the recording> [brand / product / notes]"
---
Edit this video with the **reel-edit** skill in style **Board** (`style-07`, template `board169.html`, built with
`scripts/board_build.py`, local render): $ARGUMENTS

Follow `/editing-style:edit`, but the video style is already chosen (Board, 16:9). Ask in ONE dialog only what's missing:
caption style (default **Silk**, offer the others), the brand (name, logo file, colours, url, tagline, the ask word),
which screens to show (app / website screenshots, or links to shoot), and whether there's music. Then follow SKILL.md
"style-07 Board": `local_cut.py --size 1920x1080 --gop 1` → spec.json from the transcript (raw seconds) →
`board_build.py` → contact sheet → `W=1920 H=1080 local_render.sh`. Finish with the file path and an honest
SHIP / FIX FIRST verdict (Board gate).
