---
description: Edit a video in one line - /editing-style:edit <video> [style] [caption-style] [script-style] [edits|local] [notes]. Anything you leave out is asked in a dialog.
argument-hint: "<video> [duet|ink|glow|folio|echo|skit] [velvet|volt|silk|heritage|marker] [turn|twice|flash] [edits|local] [notes]"
---
Edit this video with the **reel-edit** skill (load it first): $ARGUMENTS

1. **Parse the arguments** (any order after the video path; names or ids both work):
   - video = the first existing file path (.mov/.mp4/.m4a/.wav). "none" = no recording (text-only / music-only video).
   - video style = duet|ink|glow|folio|echo|skit or style-01…style-NN (also any user style name from `reel-library/video-styles/`)
   - caption style = velvet|volt|silk|heritage|marker or cap-01…cap-NN (or a user caption name)
   - script style = turn|twice|flash or script-01…script-NN
   - output = edits | local ; aspect = 9:16 (default) | 16:9 | 1:1 ; everything else = topic / notes / links to screenshot.
2. Read `./reel-library/` (run `/editing-style:setup` first if it's missing). **Ask only for what's missing**, in ONE
   AskUserQuestion dialog (≤ 4 questions, ≤ 4 options each, the best fit first; "Other" takes any id or name).
   Defaults if the user says "you choose": folio + its default caption, output = Edits app on macOS when the
   `metapilot-native` MCP is connected, else local.
3. Name the choices back in one line, then follow the skill's Fast path. Finish with the file path of the finished
   video and an honest SHIP / FIX FIRST / RE-RECORD verdict.
4. Save the work in `./reels/<date>-<slug>/` and offer `/editing-style:build` to keep anything new.

Example: `/editing-style:edit ~/Videos/take3.mov folio silk turn local "git reflog saves deleted commits"`
