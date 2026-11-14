# Your sound effects (local renders)

Put one file per role in this folder (`reel-library/sfx/`). `sfx_cues.py` finds every moment on a motion page that
needs a sound and `local_render.sh` mixes these files in automatically. Any audio format ffmpeg reads works.

| file name | plays on | suggested sound | volume |
|---|---|---|---|
| `whoosh.mp3` | every page cut | short sharp whoosh (0.3–0.6 s) | 0.6 |
| `popup.mp3` | every card / screenshot / tile that pops in | soft UI "pop-up" (0.3–0.5 s) | 0.5 |
| `tick.mp3` | pills, labels, date pills, speech bubbles | small notification tick | 0.4 |
| `typing.mp3` | typed text (commands, search bars) | keyboard typing loop (≥ 3 s, trimmed per cue) | 0.35 |
| `highlight.mp3` | highlighter sweeps on screenshots and quotes | light ding / notification | 0.5 |
| `hit.mp3` | a count-up landing, a hard cut on the payoff | punchy pop | 0.45 |

Missing files are skipped (the cue list tells you which). **Use only sounds you have the rights to**: your own
recordings, or CC0 / royalty-free packs (for example the CC0 filter on Freesound, or Pixabay's sound effects; check
each site's licence). The plugin does not ship audio files.

**In the Edits app you don't need this folder:** the skill adds the matching sounds from the Edits catalogue
(Whoosh (sharp), Popup (cute), Notification (pop-up), Typing (fast) 2, Pop) at every cue.

---
Library format by Tejas — https://github.com/Tejas-pr/claude-editing-style
