#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""style-07 BOARD (16:9): build motion.html from a spec.json + the cut map.

  python3 -I board_build.py spec.json REELDIR [--cap cap-03] [--size 1.0]

REELDIR holds map.json (from local_cut.py, or an Edits PLAN.map.json), face-cut.mp4 and the images the spec names
(logo, screenshots). Writes REELDIR/motion.html with the sound cues embedded (sfx_cues.py reads them, so
local_render.sh mixes them like any other page). All times in the spec are RAW recording seconds (what you read off the
transcript of the uncut take); they are mapped onto the cut timeline. Put "timeline": true in the spec to give
timeline seconds instead.

spec.json (everything except "pages" is optional):
{
  "captions": "cap-03", "size": 1.0,                       // cap-01 … cap-05, size 0.88 | 1 | 1.14
  "brand": {"name": "Acme", "logo": "logo.png", "tagline": "One line on what it is.", "url": "acme.com",
            "ask": "Comment “LINK” 👇", "comment_word": "LINK", "dm": "✈️ link sent to your DMs",
            "accent": "#D8ACAC", "deep": "#a85f66", "paper": "#f7f1e8", "ink": "#1d1416",
            "hl": "(default: the accent)", "kwlight": "#f4b9b0", "font": "Playfair Display", "demo_label": "demo account"},
  "speakers": {"a": {"label": "her 😩", "focus": [24, 32]}, "b": {"label": "him 😎", "focus": [76, 30]}},
  "hook":  {"l1": "POV: you run a small business", "l2": "and *nothing* is organised", "out": 10.7},
  "subs":  [[4.28, 5.84, "a", "Look at you, sitting all *relaxed*"], ...],      // start, end, speaker, line (*keyword*)
  "pages": [[4.22, "big", "both"], [10.72, "chaos", "a"], [32.0, "corner", "b"], [76.5, "side", "b"], [81.6, "end", "b"]],
  "punch": [[8.80, 1.16, 24, 32, 9.44]],                   // start, scale, focus x%, y%, until
  "screens": [{"t": 32.06, "img": "screens/dashboard.png", "box": [69, 28, 29, 12], "demo": true, "tag": "for creators",
               "url": "acme.com/app"}],                    // box = highlighter in % of the image (l, t, w, h)
  "emoji": [[4.28, "😎", 92, 16, "zero stress", 5.84]],    // start, emoji or sticker image, x% y% of the card, label, until
  "notes": [[10.72, "💸", "Payment pending", "2 clients haven't paid"]], "chaos": [17.66, 19.70],
  "stings": [[23.02, "big"], [30.96, "small"]], "badge": 31.0,
  "comment": [76.54, 78.12, 78.88],                         // card in, typing starts, DM line
  "end": 81.62, "tail": 1.6                                  // end card time, seconds the page runs past the footage
}
Layouts: big (talking) · chaos (card medium + notification pile) · corner (card small, screens fill the frame) ·
side (comment card) · end (logo, name, tagline, url, ask). Show "demo" on any screen with seeded / test data.
"""
import json, os, sys

def arg(k, d=None):
    a = sys.argv; return a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else d

if len(sys.argv) < 3: print(__doc__); sys.exit(1)
SPEC, OUT = json.load(open(sys.argv[1])), sys.argv[2]
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(OUT, "map.json")))
KEEP, SPEED, VDUR = M["keep"], M.get("speed", 1.0), M["end"]
RAWT = not SPEC.get("timeline")

def tl(s):
    if s is None or not RAWT: return s
    for a, b, st in KEEP:
        if a - 1e-6 <= s <= b + 1e-6: return round(st + (s - a) / SPEED, 3)
    for a, b, st in KEEP:
        if s < a: return round(st, 3)          # inside a cut gap: the next kept moment
    return VDUR

DUR = round(VDUR + float(SPEC.get("tail", 1.6)), 3)
pages = []
P = SPEC["pages"]
for i, (s, lay, foc) in enumerate(P):
    a = 0.0 if i == 0 else tl(s); b = tl(P[i + 1][0]) if i + 1 < len(P) else DUR
    pages.append({"a": a, "b": b, "layout": lay, "focus": foc})
screens = []
SC = SPEC.get("screens", [])
for i, s in enumerate(SC):
    a = tl(s["t"]); pg = next((p for p in pages if p["a"] - .01 <= a < p["b"]), pages[-1])
    nxt = next((tl(x["t"]) for x in SC[i + 1:]), None)
    b = nxt if nxt is not None and nxt < pg["b"] else pg["b"]
    if s.get("until") is not None: b = min(b, tl(s["until"]))
    screens.append({"a": a, "b": b, "img": s["img"], "box": s.get("box"), "demo": bool(s.get("demo")), "tag": s.get("tag", ""),
                    "url": s.get("url"), "rot": [-1, 1][i % 2] * .6})
hook = SPEC.get("hook")
if hook: hook = dict(hook, out=tl(hook.get("out", P[1][0] if len(P) > 1 else 3.0)))
cfg = {
  "cap": arg("--cap", SPEC.get("captions", "cap-03")), "cs": float(arg("--size", SPEC.get("size", 1.0))),
  "dur": DUR, "vdur": VDUR, "video": "face-cut.mp4", "brand": SPEC.get("brand", {}), "speakers": SPEC.get("speakers", {}),
  "hook": hook, "pages": pages, "screens": screens,
  "subs": [{"a": tl(a), "b": max(tl(b), tl(a) + .4), "who": w, "h": t} for a, b, w, t in SPEC.get("subs", [])],
  "punch": [{"t": tl(t), "s": s, "x": x, "y": y, "u": tl(u)} for t, s, x, y, u in SPEC.get("punch", [])],
  "emo": [{"t": tl(t), "e": e, "x": x, "y": y, "label": lab, "u": tl(u)} for t, e, x, y, lab, u in SPEC.get("emoji", [])],
  "notes": [{"t": tl(t), "i": i, "h": h, "s": s} for t, i, h, s in SPEC.get("notes", [])],
  "chaos": [tl(x) for x in SPEC["chaos"]] if SPEC.get("chaos") else None,
  "stings": [{"t": tl(t), "k": k} for t, k in SPEC.get("stings", [])],
  "badge": tl(SPEC.get("badge")), "comment": [tl(x) for x in SPEC["comment"]] if SPEC.get("comment") else None,
  "end": tl(SPEC.get("end")),
}

# sound cues (roles = reel-library/sfx file names; sfx_cues.py mixes them and lists the Edits catalogue sound)
cues = []
add = lambda t, r, d=0: t is not None and cues.append([round(max(0.0, t), 3), r, d])
if hook: add(0.0, "popup")
for p in pages[1:]: add(p["a"] - .12, "whoosh")                       # the card moves
for s in screens:
    add(s["a"] + .05, "popup")
    if s["box"]: add(s["a"] + 1.0, "highlight")                       # highlighter sweep
for e in cfg["emo"]: add(e["t"], "popup")
for n in cfg["notes"]: add(n["t"], "tick")
if cfg["chaos"]: add(cfg["chaos"][0], "hit")
for s in cfg["stings"]: add(s["t"], "hit" if s["k"] == "big" else "tick")
if cfg["comment"]: add(cfg["comment"][0], "popup"); add(cfg["comment"][1], "typing", .6); add(cfg["comment"][2], "tick")
add(cfg["end"], "hit")
cues.sort()

page = open(os.path.join(SK, "templates", "board169.html"), encoding="utf-8").read()
page = page.replace("/*CFG*/{}", json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/"))
page = page.replace("</body>", f'<script type="application/json" id="sfx-cues">{json.dumps(cues)}</script>\n</body>', 1)
open(os.path.join(OUT, "motion.html"), "w", encoding="utf-8").write(page)
missing = [x for x in [cfg["brand"].get("logo")] + [s["img"] for s in screens] if x and not os.path.exists(os.path.join(OUT, x))]
print(f"motion.html {cfg['cap']} x{cfg['cs']}  {DUR}s  pages={len(pages)} screens={len(screens)} subs={len(cfg['subs'])} cues={len(cues)}")
if not os.path.exists(os.path.join(OUT, "face-cut.mp4")): print("note: no face-cut.mp4 in", OUT, "(run local_cut.py --size 1920x1080 --gop 1)")
if missing: print("missing files:", ", ".join(missing))
