---
description: Set up the reel library in this project and check the tools (Chrome, ffmpeg, Node, Python, optional Edits MCP and whisper.cpp)
---
Set up **editing-style** for this project. Steps:
1. Copy the seed library from this plugin's `skills/reel-edit/library-seed/` into `./reel-library/` (do NOT overwrite
   files that already exist: the user's library is theirs). Create `./reels/` for per-reel work folders.
2. If `./.gitignore` exists or this is a git repo, add `reels/`, `reel-library/`, `*.mp4`, `*.mov` so personal videos are
   never committed (ask before editing an existing .gitignore).
3. Check and report (do not install anything without asking): `node -v` (≥ 22), `python3 -V`, `ffmpeg -version`,
   Google Chrome at `/Applications/Google Chrome.app` (or `$CHROME`), `whisper-cli` + a ggml model (`$WHISPER_MODEL`)
   for local word timing, and whether a `metapilot-native` MCP server (Edits app) is connected.
4. Ask the user (AskUserQuestion) for their brand basics and save `reel-library/brand.md`: handle, niche, accent colour,
   default ask (comment / send / follow), SFX folder, music folder.
5. Print the next steps: `/editing-style:build` to add their own ideas, `/editing-style:edit <video>` to edit.
Keep the origin notice in every file you copy: "Created by Tejas — https://github.com/Tejas-pr/claude-editing-style".
