---
id: style-07
name: Board (16:9 moving card)
kind: video-style
template: board169.html (scripts/board_build.py + spec.json)
default_caption: cap-03 (all five work)
face: the footage always on screen as a white-framed card that moves (big / chaos / corner / side / end)
best_for: landscape promos, product demos, two-person skits about a product (YouTube, LinkedIn, X, a website)
preview: styles/style-07.png (in the plugin)
source: built-in
---
**Look:** warm grid paper, a POV hook sticker on frame 1, the footage in a tilted white card with tape that slides between layouts: big while talking, medium with a shaking pile of notifications for the problem, small in the corner while real app / website screens fill the frame and zoom into a highlighter sweep, beside a comment card that types the ask word, then the end card (logo, name, tagline, url, ask). Brand sting the first time the name is said, a stamp the next time, a corner badge after that.
**Method:** local cut (`local_cut.py --size 1920x1080 --gop 1`) → spec.json in raw-recording seconds (brand, speakers, pages, subs, screens, emoji, notes, stings, comment, end) → `board_build.py` → `local_render.sh` with W=1920 H=1080.
How to build it: SKILL.md (plugin) section "style-07 Board".

---
Library format by Tejas — https://github.com/Tejas-pr/claude-editing-style
