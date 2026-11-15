---
id: style-06
name: Skit (funny skit / re-acted sound)
kind: video-style
template: none (scripts/skit_sync.py)
default_caption: the reference's title + emoji reactions
face: the take itself, full screen, with 2x close-up punch-ins
best_for: POV skits and lip-sync memes on a trending sound
preview: styles/style-06.png (in the plugin)
source: built-in
---
**Look:** the reference's title on the first shot, a quick close-up ping-pong (him / her / him / her, ~0.3 s each, 🤡 beside each face), the beat moment (stone-paper-scissors hits) landing on the sound's beats, a 😭 punch-in on the loser, the payoff line lip-synced.
**Method:** match moments, not waveforms (your take is your own voices). Anchors = words, beat hits (`skit_sync.py levels`), hand or mouth hits (`skit_sync.py motion`) → `skit_sync.py plan` gives each piece its own speed (0.7–1.3x on movement, slow-mo only on still holds, cut the sound only in quiet gaps).
How to build it: SKILL.md (plugin) section "style-06 Skit".

---
Library format by Tejas — https://github.com/Tejas-pr/claude-editing-style
