---
id: style-08
name: Series (information-video-red)
kind: video-style
template: story.html + templates/info-red/ (scripts/info_red.py)
default_caption: cap-03 (one-word chest captions, keyword red italic)
face: full screen the whole time (blur pages show the cut face cam behind the big words)
best_for: educational SERIES ("Part n of N" explainers): every part keeps the same look, chip, roadmap and cover
preview: styles/style-08.png (in the plugin)
source: built-in
---
**Look:** your face full screen; one-word chest captions (Poppins + serif italic, keyword in red); a red series chip top-left on every page (`RAG · PART 3/10`); bold colour cards for the teaching (ink = problems / numbered steps with a big red first letter, cream = acronyms and analogies, butter = the everyday example); blur pages for the big lines (the series word in giant red); Phosphor duotone stickers on white badges (never emojis); ONE running example carried through every step; a roadmap row with the current part lit; an open loop into the next part ("RAG PART 4 →" + "follow so you don't miss it" on screen only); and a **cover page as the last 0.5 s** (PART 0n of N, giant red series word, 2-line hook, B&W polaroid, stickers, curiosity note) + a 1080x1920 cover PNG to upload as the Instagram cover.
**Method:** cut (pauses, retakes, 1.15x only if it stays ≤ 190 wpm) → `words.py` + `face_cut()` → `build.py` with `info_red.Reel` (`R.S`, `R.STK`, `R.STEP`, `R.blur`, `R.road`, `R.next_part`, `R.cover`, `R.build`) → sheet with `--under face-cut.mp4` → `render.mjs --alpha` → Edits (face main track + overlay, last face piece +0.5 s for the cover, punch-ins, sounds, ONE theme song for the whole series). Series rule: once a series has this style, later parts use it without asking again.
How to build it: SKILL.md (plugin) section "style-08 Series"; runnable example `scripts/info_red_example.py`.

---
Library format by Tejas — https://github.com/Tejas-pr/claude-editing-style
