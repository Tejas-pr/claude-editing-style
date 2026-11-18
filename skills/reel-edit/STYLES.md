# Style catalogue: Duet · Ink · Glow · Folio · Echo · Skit · Board

Every style has a number AND a name; both work everywhere (`template("folio")`, `/editing-style:folio`).

At the start of EVERY edit, `/editing-style:edit` (or the reel-edit skill) asks the user in the AskUserQuestion dialog:
**1. edit style** (style-01 … style-08) · **2. caption style** + size · **3. face cam or voiceover** · **4. topic / sources to
screenshot** · **5. target length**. Never assume last reel's answers. Show the preview PNGs below if they want to see them. Users add their own styles as style-09, style-10 … with `/editing-style:build` (stored in `reel-library/`).
`reel_lib.STYLES[id]` → (template, default captions); `template("style-04")` gives the template path.

| id | name | template | default captions | face | best for | preview |
|---|---|---|---|---|---|---|
| **style-01** | **Duet** · split card | `split.html` | `serif-band` | creator card at the bottom of every split page + full-face pages | talking explainers with face cam | `styles/style-01.png` |
| **style-02** | **Ink** · paper classic | `paper.html` | `classic` | optional polaroid | voiceover-only explainers, the v2 look (Inter + Playfair) | `styles/style-02.png` |
| **style-03** | **Glow** · full-face story | `story.html` | `pop-serif` (one word at a time) | full screen the whole time | personal frameworks, "how to" with face; blur pages, colour step cards, meter, legal pad | `styles/style-03.png` |
| **style-04** | **Folio** · paper pro *(default)* | `paper.html` | `pop-serif` (headline) | moving face card: bottom polaroid / top wide / center / full / hidden | news, breakdowns, anything with sources: real tweets/IG/articles + smooth motion | `styles/style-04.png` |
| **style-05** | **Echo** · paper subtitles | `paper.html` | `pop-serif` + `.sub` lines | wide card on top (or full) | faster talking reels: one subtitle line under the media, keyword in a yellow box | `styles/style-05.png` |
| **style-06** | **Skit** · funny skit / re-acted sound | none (`scripts/skit_sync.py`) | the reference's title + emoji reactions (🤡 😭) | the take itself, full screen, with 2x close-up punch-ins | POV skits and lip-sync memes on a trending sound: your take timed to the sound piece by piece | `styles/style-06.png` |
| **style-07** | **Board** · 16:9 moving card | `board169.html` (`scripts/board_build.py` + a spec.json) | `pop-serif` headline (all 5 work) | the footage ALWAYS on screen as a white-framed card that moves: big (talking) · chaos (+ notification pile) · corner (screens fill the frame) · side (comment card) · end | landscape (YouTube, LinkedIn, X, website) promos, product demos, two-person skits about a product: real app / site screens with zoom-to-highlight, hook sticker, brand sting, end card | `styles/style-07.png` |
| **style-08** | **Series** · information-video-red | `story.html` + `templates/info-red/` (`scripts/info_red.py`) | `pop-serif` one-word chest captions, keyword red italic | full screen the whole time (blur pages use `face-cut.mp4`) | **educational SERIES** ("Part n of N"): red series chip on every page, colour step cards (letter-by-letter acronyms, numbered steps tied to one running example), blur pages for the big lines, roadmap dots, open loop into the next part, **cover page = last 0.5 s** + cover PNG | `styles/style-08.png` |

## Caption styles (ask together with the edit style)
| id | name | where it shows | size default (smaller · bigger) |
|---|---|---|---|
| cap-01 | **Velvet** (`serif-band`) | seam captions in the creator card (style-01) | 11rem (9.6 · 12.4) |
| cap-02 | **Volt** (`anton-caps`) | seam captions, hype/news (style-01) | 9.2rem (8 · 10.4) |
| cap-03 | **Silk** (`pop-serif`) | paper headline Poppins + Instrument Serif italic (style-04/05); one-word chest captions (style-03) | headline 12rem / chest 8.4rem |
| cap-04 | **Heritage** (`classic`) | paper headline Inter + Playfair bold italic (style-02) | 9.2rem |
| cap-05 | `.sub` subtitle line | under the media, Poppins 600, keyword in a yellow box (style-05, or mixed into style-04) | 5rem |

## How each style is built (all share `engine.js` + `components.css`; smooth motion is on for every page without a creator window)
- **style-01**: `.scene.split` (panel + `.creator > .hole`), `.scene.face`, `.title` per section, `.seam data-words`. Edits:
  creator transforms per window change (render prints them). See reel-edit.md "Edits assembly".
- **style-02**: `paper.html` scenes with `.l1` / `.l2` headline, cards, `.polaroid > .hole`. `captions="classic"`.
- **style-03**: `story.html` pages `.scene.story / .blur / .bw / .card / .media`, `face_cut()` for blur/bw pages. Creator full
  screen on the Edits main track, no transforms.
- **style-04**: `paper.html` + ONE `<div class="facecard" data-show="0-2.7 bottom polaroid|2.7-4.9 top wide|7.4-10.4 full|…">
  <div class="hole"></div></div>` outside the scenes. Positions `top · center · bottom · full`, shapes `polaroid · wide`;
  leave a gap in data-show to hide the face. Scenes get `f-top/f-bottom/…` automatically and lay out around the face.
  Real screenshots: `scripts/source_shot.mjs` + `.shotcard` + `.hlbox` (`.inv` = black box) + `.srcline` + `.person`.
- **style-05**: style-04 with `.sub data-words` captions instead of the headline, face card `top wide` most of the time.
- **style-06**: no motion page. Anchors (words, beats, hand hits) → `skit_sync.py plan skit.json` → speeds per piece,
  2x close-up punch-ins, sound cuts only in quiet gaps, title + emoji texts in Edits (or `skit_sync.py render` locally).
  Full recipe: SKILL.md "style-06 Skit".
- **style-07**: local render, no Edits needed. `local_cut.py RAW reels/<slug> --size 1920x1080 --gop 1` → spec.json
  (brand, pages, subs, screens …; `scripts/board_spec_example.json`) → `board_build.py spec.json reels/<slug>` →
  `W=1920 H=1080 local_render.sh motion.html face-cut.mp4 final.mp4 [music] [vol] [sfx_dir]`. Full recipe: SKILL.md "style-07 Board".
- **style-08**: `from info_red import Reel` → `R = Reel(HERE, W, series, part, parts, speech_end)`; pages with `R.scene("story"|"card ink"|"card cream"|"card", a, b, body)`, `R.blur()`, `R.S()` chest captions, `R.STK()` stickers, `R.STEP()` step cards, `R.road()`, `R.next_part()`, `R.cover()` then `R.build()`. Shared CSS / stickers / cover: `templates/info-red/`. Runnable example: `scripts/info_red_example.py`. Full recipe: SKILL.md "style-08 Series".

## Edits recipe for the moving face card (style-04/05), verified
1. Render `motion.mov --alpha`; it prints every face-window change `time {x,y,w,h}` (null = hidden).
2. Edits: `addMedia face.mp4` (main track), `addOverlay motion.mov` (0, .5, .5, 1), `splitAt` the face clip at every change.
3. `setTransforms` per piece (f = face centre height in the raw frame, about 0.30 for a seated face cam; fx = face x):
   - polaroid (w .5505, h .3409; centre y .6875 bottom, .3177 top): **scale 0.56, x 0.5, y = centre − (fy − 0.5)×0.56**
     with fy = the frame height you want centred (≈ 0.555 for a phone face cam: hair at ≈ 0.30, chest at ≈ 0.85), so
     **bottom y 0.657, top y 0.287**. Shows the whole head and shoulders. The old 0.62 / y .774 recipe cut the hair;
     x must stay 0.5 at 0.56 or the card shows an edge.
   - **Prefer polaroid over wide top for face pages:** a 9:16 face cannot fill the 16:10 wide card without cropping the
     chin or forehead. Use `top polaroid` when the face must sit on top.
   - wide top (w .8148, h .2865, centre y .2839): scale = w×1.04 = 0.847, x 0.5, y = 0.2839 + (0.5 − f)×0.847
   - full: scale 1, x .5, y .5 · hidden pieces: anything (the paper covers them)
   Always check the scaled video still covers the window: x ± scale/2 must contain hole.x ± w/2.
4. `frameSheet` at one time per window → adjust → `saveProject` → export 2K High.

---
Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
