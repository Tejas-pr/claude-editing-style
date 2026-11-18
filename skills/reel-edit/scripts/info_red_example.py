# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""style-08 Series: a complete, runnable example ("API · Part 1 of 5", ~15 s) with hand-written word times.

    python3 info_red_example.py OUT_DIR
    node render.mjs OUT_DIR/motion.html OUT_DIR/sheet.png --stills 0.5,3.3,5.5,9,11.8,14,15.7   # quick check
    node render.mjs OUT_DIR/motion.html OUT_DIR/motion.mov --alpha                            # overlay for your face cam

In a real reel, W comes from the transcript + PLAN.map.json (`reel_lib.words(RAW, tl)`), not from this list, and
`face-cut.mp4` (reel_lib.face_cut) is the cut face cam that blur pages show behind the big words. Here both are optional:
without face-cut.mp4 the blur page is just dark, and a grey placeholder is written for the cover photo.
"""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from info_red import Reel, RED, INK, BLUE, GREEN, AMBER, PURPLE

OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "info-red-example")
os.makedirs(OUT, exist_ok=True)

# (word, timeline seconds). "word*" is not used here: keywords are passed to S(..., keys=(index, ...)).
W = [("How",.2),("does",.42),("your",.6),("weather",.8),("app",1.2),("know",1.5),("it's",1.9),("raining?",2.1),   # 0-7
     ("It",2.8),("asks",3.0),("an",3.3),("API.",3.5),                                                              # 8-11
     ("Application",4.0),("Programming",4.8),("Interface.",5.6),                                                   # 12-14
     ("Think",6.6),("of",6.85),("a",6.95),("waiter",7.1),("in",7.6),("a",7.72),("restaurant.",7.9),                # 15-21
     ("You",8.8),("order,",9.0),("the",9.6),("waiter",9.75),("tells",10.2),("the",10.45),("kitchen,",10.6),         # 22-28
     ("and",11.3),("brings",11.5),("your",11.85),("food.",12.0),                                                   # 29-32
     ("But",12.5),("how",12.75),("does",12.95),("it",13.15),("talk?",13.3),("That's",14.0),("Part",14.4),("2.",14.75)]  # 33-40

R = Reel(OUT, W, series="API", part=1, parts=5, speech_end=15.4)
t, S, SVG, STK, scene = R.t, R.S, R.SVG, R.STK, R.scene
A, B, C, D, E = 0, 2.7, 3.9, 6.45, 12.4

CSS = """
.prob{font:800 11rem/1 var(--pop);letter-spacing:-.05em;color:#fff;text-shadow:0 .3rem 1.6rem rgba(0,0,0,.45)}
.scene.card.ink .trow span{color:#fff;font-size:7rem}
"""

scenes = [
  # hook, readable at frame 1 (the top line is on screen from 0.0 s)
  scene("story", A, B,
    '<div class="top"><div class="hookt"><span class="s">your weather app</span><span class="b">knows it’s <span class="r">raining</span>?</span></div>'
    f'<div class="row" style="gap:2.4rem;margin-top:1.4rem">{STK("sun", AMBER, 0, 13, -8, anim="none")}{STK("robot", BLUE, t(5), 13, 6)}</div></div>'
    + S(0, 7, keys=(5, 7))),
  # blur page: the big line
  R.blur(B, C, [("it asks", t(8)), ("an API", t(10,-.05), "kw ragw sm")],
    f'<div class="sparks">{STK("sparkle", AMBER, t(11), 10, -10)}</div>'),
  # acronym card, letter by letter on the spoken word
  scene("card cream", C, D,
    '<div class="stephead"><span>what it stands for</span></div><div class="acro">'
    + "".join(f'<div class="arow" data-in="{t(i,-.05)}" data-anim="rise"><span class="L">{L}</span>'
              f'<span class="wd" data-in="{t(i)}" data-anim="blur">{rest}</span></div>'
              for i, L, rest in [(12, "A", "pplication"), (13, "P", "rogramming"), (14, "I", "nterface")])
    + '</div>'),
  # step card with the running example (the waiter), analogy chip at the bottom
  R.STEP(1, "W", "aiter", f'<span data-in="{t(15)}" data-anim="fade">an API is the <em>waiter</em></span>',
    f'<span data-in="{t(32)}" data-anim="pop">app = you · server = kitchen · <b>API = waiter</b></span>', D, E,
    '<div class="trows" style="top:80rem">'
    f'<div class="trow" data-in="{t(22,-.05)}" data-anim="rise">{STK("chat-circle-text", PURPLE, t(22,-.05), 13, -5, anim="none")}<span>you order</span></div>'
    f'<div class="trow" data-in="{t(26,-.05)}" data-anim="rise">{STK("arrow-right", INK, t(26,-.05), 13, 5, anim="none")}<span>it tells the kitchen</span></div>'
    f'<div class="trow" data-in="{t(30,-.05)}" data-anim="rise">{STK("check-circle", GREEN, t(30,-.05), 13, -4, anim="none")}<span>food comes back</span></div>'
    '</div>', of=3),
]
# open loop into the next part + the series roadmap (part 1 lit)
nx = R.next_part(E, t(39,-.1), t(37), S(33, 40, keys=(37, 39, 40)))
scenes.append(nx.replace('<div class="hw"', R.road(t(33)) + '<div class="hw"', 1))

face = os.path.join(OUT, "cover-face.jpg")
if not os.path.exists(face):   # placeholder: replace with a B&W still of the creator (see SKILL.md "style-08 Series")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x777777:s=1000x1080", "-frames:v", "1", face], check=False)
R.cover(line_a="What is an", line_b="API, really?", kicker="DEV SERIES", note="a waiter?!", steps="request<i>→</i><b>A</b>PI<i>→</i>response",
        stickers=[("robot", BLUE, 15, 10), ("chat-circle-text", PURPLE, 17, -8), ("check-circle", GREEN, 13, 7),
                  ("sparkle", AMBER, 9, -12), ("arrow-right", RED, 12, -6)])
R.build(scenes, page_title="API part 1", css=CSS)
print("wrote", os.path.join(OUT, "motion.html"), "end", R.end)
