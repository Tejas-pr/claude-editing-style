# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Helpers for building a reel motion page (split.html / paper.html) from transcript word times.
Import from a per-reel build.py:   import sys; sys.path.insert(0, SKILL_SCRIPTS); from reel_lib import *

  tl, END = load_map("vo.map.json")              # original timeline s -> finished timeline s (cuts + speed)
  W = words([("Don't",1.06),("rewrite",1.38),(None,2.06),...], tl)   # None = spoken filler not shown on screen
  seam(W, 0, 6, keys={4})                        # data-words string for a .seam (keys -> keyword colour)
  cap(W, 0, 4, keys=[4], col="accent", tin=0, tout=2.1, hook=True)   # big caption stack html
  title("Discord Deleted", "94% Of Its Code", tin=0, tout=12, acc="Deleted")
  assemble(template("paper"), OUT, scenes=[...], captions="pop-serif")   # writes OUT + copies components.css, engine.js
The Discord reel (b-rools/discord-video-player/build.py) is a worked example of the paper variant.
"""
import html, json, os, shutil

def load_map(path):
    M = json.load(open(path)); K, SP = M["keep"], M["speed"]
    def tl(t):
        for a, b, s in K:
            if a - .02 <= t <= b + .02: return s + (max(t, a) - a) / SP
        a, b, s = min(K, key=lambda k: min(abs(t - k[0]), abs(t - k[1])))
        return s + (min(max(t, a), b) - a) / SP
    return tl, M.get("end")

def words(raw, tl): return [(w, round(tl(t), 3)) for w, t in raw]

def seam(W, a, b, keys=()):
    return "|".join(f"{W[i][1]:.2f} {html.escape(W[i][0])}{'*' if i in keys else ''}" for i in range(a, b + 1) if W[i][0])

def cap(W, a, b, keys=(), col="accent", tin=None, tout=None, hook=False, cls=""):
    """Caption stack: filler words small (sans), keyword words on their own big serif line. hook=True shows the
    filler at frame 0 and ghosts the keyword from frame 0 (the first frame must already carry the hook)."""
    tin = W[a][1] - .08 if tin is None else tin; parts, line, i = [], [], a
    def flush():
        if line: parts.append('<span class="ln">' + "".join(line) + "</span>"); line.clear()
    while i <= b:
        w, t = W[i]
        if w is None: i += 1; continue
        if i in keys:
            flush(); kw, n = [], 0
            while i <= b and (i in keys or W[i][0] is None):
                if W[i][0]:
                    kw.append(f'<span class="w" data-t="{W[i][1]:.2f}"' + (' data-g="-1"' if hook else '') + f'>{html.escape(W[i][0])}</span>'); n += len(W[i][0]) + 1
                i += 1
            fs = 15 if n <= 9 else 12.5 if n <= 12 else 10.5 if n <= 15 else 8.8
            parts.append(f'<span class="ln kw {col}" style="font-size:{fs}rem">' + " ".join(kw) + "</span>"); continue
        line.append(f'<span class="w" data-t="{0 if hook else t:.2f}">{html.escape(w)} </span>'); i += 1
    flush()
    return f'<div class="cap {cls}" data-cin="{tin:.2f}" data-cout="{tout:.2f}">' + "".join(parts) + "</div>"

def title(t1, t2, tin, tout, acc=None):
    if acc: t1 = t1.replace(acc, f'<span class="acc">{acc}</span>', 1)
    return f'<header class="title" data-in="{tin:.2f}" data-out="{tout:.2f}"><span class="t1">{t1}</span><span class="t2">{t2}</span></header>'

CAPTION_STYLES = ("serif-band", "anton-caps", "pop-serif", "classic")   # classic = paper v2 look (no caption css)   # approved caption styles (templates/captions/*.css); serif-band = house default
# edit styles -> template. the dialog asks which one at the start of every edit.
# EDIT STYLES (numbered, like caption styles). the dialog asks which one at the start of every edit.
# Catalogue with previews: skills/reel-edit/STYLES.md. id -> (template, default captions)
STYLES = {
  "style-01": ("split.html", "serif-band"),  # DUET · Duet (split card): grid-paper panel on top, creator card at the bottom, seam captions
  "style-02": ("paper.html", "classic"),     # INK · Ink (paper classic): headline (Inter + Playfair) + cards, voiceover, face in a polaroid
  "style-03": ("story.html", "pop-serif"),   # GLOW · Glow (full-face story): creator full screen, blur pages, colour step cards, meter, legal pad
  "style-04": ("paper.html", "pop-serif"),   # FOLIO · Folio (default): headline + real screenshots + smooth motion + moving face card
  "style-05": ("paper.html", "pop-serif"),   # ECHO · Echo (paper subtitles): face card wide on top, subtitle line under the media (.sub)
  "style-06": (None, None),                  # SKIT · Skit (funny skit / re-acted trending sound): no motion page, scripts/skit_sync.py
}
STYLE_NAMES = {"duet": "style-01", "ink": "style-02", "glow": "style-03", "folio": "style-04", "echo": "style-05", "skit": "style-06"}
CAPTION_NAMES = {"velvet": "serif-band", "volt": "anton-caps", "silk": "pop-serif", "heritage": "classic"}   # marker = .sub lines
EDIT_STYLES = {k: v[0] for k, v in STYLES.items()} | {n: STYLES[i][0] for n, i in STYLE_NAMES.items()} | {"split": "split.html", "paper": "paper.html", "story": "story.html"}
def template(style):
    if EDIT_STYLES[style] is None: raise ValueError(f"{style} has no motion template: build it with scripts/skit_sync.py")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", EDIT_STYLES[style])


def face_cut(raw, map_path, out, offset=0.0, w=1440, h=2560, fps=30):
    """style-03 blur / bw pages: timeline-aligned copy of the cut creator footage (video.face data-src). raw = face cam,
    map_path = PLAN.map.json (keep [a, b, timeline start] + speed), offset = original-timeline s minus source s.
    Silent, every frame a keyframe (-g 1) so headless Chrome seeks frame-exact."""
    import subprocess
    M = json.load(open(map_path)); K, SP = M["keep"], M["speed"]
    parts = [f"[0:v]trim=start={a - offset:.4f}:end={b - offset:.4f},setpts=(PTS-STARTPTS)/{SP}[v{i}]" for i, (a, b, st) in enumerate(K)]
    fc = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(K))) + f"concat=n={len(K)}:v=1:a=0,fps={fps}," \
         f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}[out]"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", raw, "-filter_complex", fc, "-map", "[out]", "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-g", "1", "-pix_fmt", "yuv420p", out], check=True)
    return out

ASPECT_CSS = {"16:9": "html{font-size:calc(100vh/108)}.scene{padding:9rem 14rem 6rem!important;gap:3.2rem!important}"
                       ".l1{font-size:4.4rem!important}.l2{font-size:9.6rem!important;margin-top:-1.4rem!important}",
              "1:1": "html{font-size:calc(100vh/108)}.scene{padding:9rem 8rem 6rem!important}"}
def assemble(template, out, scenes, titles=(), css="", page_title="Reel motion", captions="serif-band", aspect="9:16"):
    """aspect: 9:16 (default, frame 108x192rem) | 16:9 (192x108rem) | 1:1 (108x108rem). Render with matching
    render.mjs --w/--h (16:9: --w 3840 --h 2160 for a 4K Edits canvas, 1920x1080 for a check)."""
    css = ASPECT_CSS.get(aspect, "") + "\n" + css
    """captions: one of CAPTION_STYLES (None = the bare components.css look, not approved for posting)."""
    captions = CAPTION_NAMES.get(str(captions).lower(), captions) if captions else captions
    if captions and captions != "classic":
        if captions not in CAPTION_STYLES: raise ValueError(f"caption style {captions!r} not in {CAPTION_STYLES}")
        css = open(os.path.join(os.path.dirname(os.path.abspath(template)), "captions", captions + ".css")).read() + "\n" + css
    src = open(template).read()
    a = src.index("<!-- ============================ SCENES"); b = src.index("<!-- ============================ END SCENES")
    src = src[:a] + "<!-- ============================ SCENES -->\n" + "\n\n".join(scenes) + "\n" + src[b:]
    if "<!-- ============================ TITLES" in src:
        a = src.index("<!-- ============================ TITLES"); b = src.index("<!-- ============================ END TITLES")
        src = src[:a] + "<!-- ============================ TITLES -->\n" + "\n".join(titles) + "\n" + src[b:]
    src = src.replace("</style>", css + "</style>", 1).replace("<title>Reel motion</title>", f"<title>{html.escape(page_title)}</title>")
    ORIGIN_STAMP = "<!-- made with claude-editing-style by Tejas · https://github.com/Tejas-pr/claude-editing-style -->"
    src = src.replace("<head>", "<head>\n" + ORIGIN_STAMP, 1)
    open(out, "w").write(src)
    d = os.path.dirname(os.path.abspath(template)); od = os.path.dirname(os.path.abspath(out))
    for f in ("components.css", "engine.js"):
        if os.path.exists(os.path.join(d, f)) and d != od: shutil.copy(os.path.join(d, f), os.path.join(od, f))
