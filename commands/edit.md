---
description: Edit a video in one of your saved styles - asks which video style, caption style, script style and output (Edits app or local render), then builds the reel
argument-hint: "<path to the recording or voiceover> [topic / notes]"
---
Edit this video with the **reel-edit** skill (load it first): $ARGUMENTS

1. Read `./reel-library/INDEX.md` and the cards (video-styles, caption-styles, script-styles, reel-ideas, brand.md).
   If the library is missing, run the setup steps from `/editing-style:setup` first.
2. Ask with ONE AskUserQuestion dialog (≤ 4 questions, ≤ 4 options each, the best-fitting first; "Other" takes any id):
   video style · caption style (+ size) · script style (only if a script is needed) · output (Edits app / local render).
   Then ask in text: face cam or voiceover, where the face sits per page, which sources to screenshot, which reel idea
   to follow, target length.
3. Follow the skill's Fast path for the chosen output and styles. Give an honest SHIP / FIX FIRST / RE-RECORD verdict.
4. Save the result in `./reels/<date>-<slug>/` and offer to store anything new with `/editing-style:build`.
