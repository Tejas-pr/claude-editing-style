# Changelog

New styles land here first. Update with `claude plugin marketplace update claude-editing-style` and
`claude plugin update editing-style@claude-editing-style`, then run `/editing-style:update` in your project.

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
