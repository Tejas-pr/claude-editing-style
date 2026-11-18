---
description: Edit a video in Series (style-08) — educational "Part n of N" series: face full screen, red series chip, step cards, blur pages, roadmap, open loop and a cover frame at the end
argument-hint: "<path to the recording> [series word] [part n of N] [topic / notes]"
---
Edit this video with the **reel-edit** skill in style **Series** (`style-08`, information-video-red: `story.html` +
`templates/info-red/`, built with `scripts/info_red.py`): $ARGUMENTS

Follow `/editing-style:edit`, but the video style is already chosen (Series). Ask in ONE dialog only what's missing:
the series word (e.g. RAG, API) and part n of N, the cover hook (2 short lines), the theme song for the whole series
(the same one on every part), and output (Edits app / local render). If an earlier part of this series exists in
`./reels/`, reuse its series word, colours, theme song and cover layout without asking. Then follow SKILL.md
"style-08 Series" (start from `scripts/info_red_example.py`), run the captions check before building motion, and
finish with the reel, the cover PNG path and an honest SHIP / FIX FIRST / RE-RECORD verdict (Series gate).
