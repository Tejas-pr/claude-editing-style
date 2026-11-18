# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""style-08 · Series (information-video-red): educational SERIES reels ("Part n of N" explainers).

Look: the creator full screen (style-03 story engine) + one-word chest captions (cap-03 pop-serif, keyword red italic),
colour step cards (ink / cream / butter), blur pages for the big lines, Phosphor duotone stickers on white badges,
a persistent series chip top-left (red box with the series word + "PART n/N"), an open-loop ending into the next part
and a COVER page as the last 0.5 s (the Instagram cover frame) + a 1080x1920 cover PNG.

    import sys, os; sys.path.insert(0, os.path.join(SK, "scripts"))        # SK = the reel-edit skill folder
    from info_red import Reel, RED, INK, BLUE, GREEN, AMBER, PURPLE
    from words import W                                   # [(word, timeline t)] via reel_lib.words + PLAN.map.json
    R = Reel(HERE, W, series="API", part=1, parts=5, speech_end=46.5)
    t, S, STK, scene = R.t, R.S, R.STK, R.scene
    scenes = [scene("story", 0, 3.1, '<div class="top">…</div>' + S(0, 9, keys=(4,))), …,
              R.STEP(1, "R", "equest", line, chip, a, b, body, of=2), R.blur(a, b, [("text", t(i)), ("KEY", t(j), "kw")]), …,
              R.next_part(a, i_part_word, i_follow, S(…))]
    R.cover(line_a="What is an", line_b="API, really?", note="waiter?!", steps="…", stickers=[("robot", BLUE, 17, -8), …])
    R.build(scenes, page_title="API part 1")             # writes motion.html (+ components.css, engine.js) with the cover appended
Then: render.mjs motion.html motion.mov --alpha · cover PNG: render the last 0.5 s (see SKILL.md "style-08 Series").
Full example: scripts/info_red_example.py.
"""
import os, sys, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reel_lib import seam, assemble, template

TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "info-red")
RED, INK, BLUE, GREEN, AMBER, PURPLE = "#ff2f4b", "#222", "#2f6fdb", "#22a35a", "#f0a400", "#7b4fe0"
FACE = '<video class="face" data-src="face-cut.mp4" data-in="0" data-from="0" data-anim="none"></video>'
# default cover sticker spots (class s1..s5 in info-red.css): pdf top-right, robot right, magnifier, sparkle, chat
DEFAULT_COVER_STICKERS = [("file-pdf", RED, 15, 10), ("robot", BLUE, 17, -8), ("magnifying-glass", INK, 13, 7),
                          ("sparkle", AMBER, 9, -12), ("chat-circle-text", PURPLE, 12, -6)]


class Reel:
    def __init__(self, here, W, series="RAG", part=1, parts=10, speech_end=None, cover_len=0.5):
        self.here, self.W, self.series, self.part, self.parts = here, W, series, part, parts
        self.speech_end = speech_end if speech_end is not None else round(max(t for _, t in W) + .5, 2)
        self.cover_len = cover_len; self.end = round(self.speech_end + cover_len, 3); self._cover = None
        self.FACE = FACE

    # word time (+ offset)
    def t(self, i, d=0.0): return round(self.W[i][1] + d, 2)

    # one-word chest captions for a story page (word* = keyword, red italic)
    def S(self, a, b, keys=(), end=None):
        e = f' data-end="{end}"' if end else ''
        return f'<div class="seam" data-max="1"{e} data-words="{seam(self.W, a, b, keys=set(keys))}"></div>'

    # Phosphor duotone icon: per-reel stickers/ folder first, then the shared templates/info-red/stickers/
    def SVG(self, name):
        for d in (os.path.join(self.here, "stickers"), os.path.join(TPL, "stickers")):
            p = os.path.join(d, name + ".svg")
            if os.path.exists(p): return open(p).read().replace('<svg ', '<svg class="ico" ', 1)
        raise FileNotFoundError(f"sticker {name}: curl -o {TPL}/stickers/{name}.svg "
                                f"https://unpkg.com/@phosphor-icons/core@2.1.1/assets/duotone/{name}-duotone.svg")

    def STK(self, name, color, tin, size=18, rot=0, anim="pop", label=None, cls=""):
        lab = f'<b>{label}</b>' if label else ''
        return (f'<div class="stkw {cls}" data-in="{tin}" data-anim="{anim}"><div class="stk" style="--c:{color};--r:{rot}deg;--s:{size}rem">'
                + self.SVG(name) + f'</div>{lab}</div>')

    @staticmethod
    def scene(kind, a, b, body, extra=""): return f'<section class="scene {kind}" data-in="{a}" data-out="{b}" {extra}>\n{body}\n</section>'
    @staticmethod
    def W_(s, tt): return f'<span class="w" data-t="{tt}">{s}</span>'

    # blur page: lines = [(text, t), (text, t, "kw"), (text, t, "kw ragw"), …] ; extra = stickers etc.
    def blur(self, a, b, lines, extra=""):
        ls = "".join(f'<span class="ln{(" " + x[2]) if len(x) > 2 else ""}">{self.W_(x[0], x[1])}</span>' for x in lines)
        return self.scene("blur", a, b, FACE + f'<div class="capbox"><div class="cap" data-cin="{a}" data-cout="{b}">{ls}</div></div>' + extra)

    # numbered step card (ink): big red letter + word, the line under it, body in the middle, analogy chip at the bottom
    def STEP(self, n, letter, word, line, chip, tin, tout, body, of=3, cls="ink"):
        return self.scene(f"card {cls} rstep", tin, tout,
          f'<div class="stephead"><span>step {n} of {of}</span><span class="prog" data-n="{of}" data-on="{n}"></span></div>'
          f'<div class="sh"><span class="big"><b>{letter}</b>{word}</span><span class="line">{line}</span></div>'
          + body + f'<div class="tchip">{chip}</div>')

    # series roadmap row (part n lit)
    def road(self, tin):
        return (f'<div class="road" data-in="{tin}" data-anim="rise">'
                + "".join(f'<i class="{"on" if k == self.part else ""}">{k}</i>' for k in range(1, self.parts + 1)) + '</div>')

    # last story page: "SERIES PART n+1 →" + on-screen follow line (the only ask)
    def next_part(self, a, t_part, t_follow, seam_html, follow="follow so you don't miss it"):
        nxt = f'PART {self.part + 1} <i>→</i>' if self.part < self.parts else 'THE END <i>✓</i>'
        return self.scene("story", a, self.speech_end,
          f'<div class="top"><div class="nextp" data-in="{t_part}" data-anim="pop"><span class="rag">{self.series}</span>{nxt}</div>'
          f'<div class="hw" data-in="{t_follow}" data-anim="fade">{html.escape(follow)}</div></div>' + seam_html)

    # the cover page (last 0.5 s). line_b = serif italic yellow line; steps = small bottom strip (HTML ok)
    def cover(self, line_a, line_b, note="", steps="", face="cover-face.jpg", polaroid="explained like you're 12",
              kicker="AI SERIES", stickers=None):
        stk = "".join(f'<div class="cv-stk s{i + 1}"><div class="stk" style="--c:{c};--r:{r}deg;--s:{s}rem">{self.SVG(n)}</div></div>'
                      for i, (n, c, s, r) in enumerate(stickers or DEFAULT_COVER_STICKERS))
        body = open(os.path.join(TPL, "cover.html")).read()
        for k, v in dict(PART2=f"{self.part:02d}", PARTS=self.parts, KICKER=kicker, SERIES=self.series, LINE_A=line_a,
                         LINE_B=line_b, FACE=face, POLAROID=html.escape(polaroid), STICKERS=stk, NOTE=note, STEPS=steps).items():
            body = body.replace("{" + k + "}", str(v))
        self._cover = self.scene("cover", self.speech_end, self.end, body, extra='data-exit="cut" data-drift="0"')
        return self._cover

    def build(self, scenes, page_title=None, css="", out="motion.html"):
        titles = [f'<header class="title series" data-in="0" data-out="{self.speech_end}"><span class="rag">{self.series}</span>'
                  f'<span class="pt">PART {self.part}<i>/{self.parts}</i></span></header>']
        if self._cover is None: raise RuntimeError("call R.cover(...) before R.build(): every style-08 reel ends on its cover")
        allcss = open(os.path.join(TPL, "info-red.css")).read() + "\n" + css
        assemble(template("style-08"), os.path.join(self.here, out), scenes=list(scenes) + [self._cover], titles=titles,
                 css=allcss, page_title=page_title or f"{self.series} part {self.part}", captions="pop-serif")
        return self.end
