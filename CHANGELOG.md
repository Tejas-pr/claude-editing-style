# Changelog

New styles land here first. Update with `claude plugin marketplace update claude-editing-style` and
`claude plugin update editing-style@claude-editing-style`, then run `/editing-style:update` in your project.

## 1.5.0 — 2026-11-18
- **New style: Series (style-08, information-video-red)** · `/editing-style:series` — for educational "Part n of N"
  series. You full screen with one-word chest captions (keyword in red), a red series chip on every page
  (`RAG · PART 3/10`), bold colour cards for the teaching (problem / step cards with a big red first letter, acronyms that
  land letter by letter, the everyday example), blur pages for the big lines, Phosphor stickers (never emojis), a roadmap
  row with the current part lit, an open loop into the next part, and a **cover page as the last 0.5 s** plus a
  1080x1920 cover PNG to upload as the Instagram cover. Series rule: later parts keep the style without asking again.
- New `scripts/info_red.py` (the `Reel` helper: chest captions, stickers, step cards, blur pages, roadmap, next part,
  cover), `scripts/info_red_example.py` (a runnable "API · Part 1 of 5" demo), `templates/info-red/` (CSS, cover page,
  32 Phosphor duotone stickers, MIT).
- Lessons: Edits caches media by path (import re-renders under a new name), per-reel CSS must not reuse engine class
  names (`.bar` crashes the render), a softly said word can be cut as a pause (always run the captions check), music on
  a beat: slip the theme song so the series-word reveal lands on a downbeat (`beatMarkers`).
- Your own `/build` styles now start at **style-09**. If you already saved a style-08, `/editing-style:update` keeps yours
  and copies Series under the next free number (the name "series" still works).

## 1.4.0 — 2026-11-18
- **New style: Board (style-07)** · `/editing-style:board` — 16:9 for YouTube, LinkedIn, X or a website. The footage is
  always on screen as a white-framed card that moves (big while talking, medium with a shaking notification pile, small in
  the corner while real app / site screens zoom into a highlighter sweep, beside a comment card that types the ask word),
  then an end card. Hook sticker, emoji on the card, brand sting + stamp + corner badge, any of the 5 caption styles.
  Brand (name, logo, colours, font, url, ask word) comes from one `spec.json`. Local render, no Edits needed.
- New `templates/board169.html`, `scripts/board_build.py` (spec.json in raw-recording seconds → motion.html with its
  sound cues embedded) and `scripts/board_spec_example.json`.
- `local_cut.py --size WxH --gop N` (16:9 / 4K footage, all-intra for frame-exact pages); `sfx_cues.py` reads cues a page
  embeds, so `local_render.sh` mixes Board's sounds like any other page (`W=1920 H=1080`).
- Your own `/build` styles now start at **style-08**. If you already saved a style-07, `/editing-style:update` keeps yours
  and copies Board under the next free number (the name "board" still works).

## 1.3.1 — 2026-11-18
- **Face card fix (style-04/05):** new polaroid transform (scale 0.56, x 0.5, bottom y 0.657 / top y 0.287) shows the
  whole head and shoulders; the old one cut the hair. Prefer a top polaroid over the wide top card for faces.
- **Pace check before speed-up:** measure words per second after the pause cut; fast talkers stay at 1.0x.
- **Export:** the folder must exist, export raw → loudness pass → delete the raw (Edits' raw export can clip).
- New lessons: one take per reel, cutout off on busy backgrounds, full-face headline layering, live timeline edits,
  fewer sounds (about half the cues), `seek` failures. Stickers instead of emojis on motion pages; caption rules.

## 1.3.0 — 2026-11-15
- **New style: Skit (style-06)** · `/editing-style:skit` — funny skits and lip-sync memes on a trending sound. Your take
  is your own voices, so it matches moments instead of waveforms: words, beat hits and hand hits become anchors, and
  each piece between them gets its own speed. Close-up ping-pong punch-ins, 🤡 / 😭 emoji reactions, sound cuts only
  in quiet gaps, slow-mo only on still holds. Works in the Edits app or with a local render.
- New `scripts/skit_sync.py`: `levels` (beat hits in the sound), `motion` (hand / mouth hits and still poses in the take),
  `plan` (speeds per piece from anchor pairs, flags anything outside 0.7–1.3x), `render` (local cut with close-ups + sound).
- Your own `/build` styles now start at **style-07**. `/update` never overwrites a user card that already uses a
  built-in id: the built-in goes to the next free number and keeps its name.

## 1.2.0 — 2026-11-15
- **Sound on every moment:** `sfx_cues.py` reads the motion page and lists every cue (page cuts, popups, pills,
  typing, highlights, count hits) with the matching Edits catalogue sound; local renders mix your `reel-library/sfx/`
  files automatically (`local_render.sh … [music] [vol] [sfx_dir]`). Voice + ducked music + SFX in one pass.
- One-time setup guide in the README; companion skill recommendation (instagram-agent-skill, MIT).
- README demo now has full sound (Edits catalogue SFX).

## 1.1.0 — 2026-11-15
- Every style has a name and its own command: **Duet** (style-01), **Ink** (style-02), **Glow** (style-03),
  **Folio** (style-04, default), **Echo** (style-05). Caption styles: **Velvet**, **Volt**, **Silk**, **Heritage**,
  **Marker**. Script styles: **Turn**, **Twice**, **Flash**.
- One-line edits: `/editing-style:edit <video> <style> <captions> [script] [edits|local]` — only missing choices are asked.
- `/editing-style:update` pulls new built-in styles into your library without touching your own.
- 16:9 and 1:1 supported (README demo video is 16:9 Folio).
- Demo video at the top of the README.

## 1.0.0 — 2026-11-15
- First release: 5 video styles, 5 caption styles, 3 script styles, `/build` library trainer, Edits app + local render.

---
Created by Tejas — https://github.com/Tejas-pr/claude-editing-style
