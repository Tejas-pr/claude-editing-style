# Changelog

New styles land here first. Update with `claude plugin marketplace update claude-editing-style` and
`claude plugin update editing-style@claude-editing-style`, then run `/editing-style:update` in your project.

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
