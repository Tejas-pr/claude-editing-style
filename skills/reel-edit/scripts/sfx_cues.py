#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""SOUND CUES: read a motion page and list EVERY moment that needs a sound effect, so none is missed.

  python3 -I sfx_cues.py motion.html                      # print the cue sheet + write cues.json next to the page
  python3 -I sfx_cues.py motion.html --mix SFX_DIR sfx.wav  # also render all cues into one sound track (local render)

Roles (what triggers them on the page)              Edits catalogue sound (searchSoundEffects)   file in SFX_DIR   volume
  whoosh     every page cut (scene data-in, not 0)   "Whoosh (sharp)"        id 775634582300210    whoosh.*          0.6
  popup      a card/screenshot/tile/code block that  "Popup (cute)"          id 1810114083746470   popup.*           0.5
             pops/blurs/zooms in (data-anim pop|blur|zoom, or rise on a card)
  tick       a pill, label, date pill, bubble, chip  "Notification (pop-up)" id 1488519876118528   tick.*            0.4
  typing     typed text (.type data-t data-dur)      "Typing (fast) 2"       id 1804165963804581   typing.*          0.35
  highlight  highlighter sweeps (mark, .hlbox)        "Notification (pop-up)" id 1488519876118528   highlight.*       0.5
  hit        a count-up landing / data-exit="cut"    "Pop"                   id 1946614579464123   hit.*             0.45
In Edits: addSoundEffect {effect: id} → move to the cue time → setVolume (typing: trim to its duration).
Cues closer than 0.12 s with the same role are merged. Times are timeline seconds (the page's own clock).
"""
import html.parser, json, os, subprocess, sys, glob

ROLES = {
  "whoosh":    ("Whoosh (sharp)", "775634582300210", .6),
  "popup":     ("Popup (cute)", "1810114083746470", .5),
  "tick":      ("Notification (pop-up)", "1488519876118528", .4),
  "typing":    ("Typing (fast) 2", "1804165963804581", .35),
  "highlight": ("Notification (pop-up)", "1488519876118528", .5),
  "hit":       ("Pop", "1946614579464123", .45),
}
TICK = {"pill", "tagline", "datepill", "bubble", "chip", "badge", "srcline-pill", "note"}
CARD = {"card", "shotcard", "phonecard", "qcard", "polaroid", "stat", "quote", "news", "code", "ui", "shot", "bars", "big",
        "phone", "person", "profile", "notif", "searchbar", "meter", "roll", "col", "row", "wide"}

class P(html.parser.HTMLParser):
    def __init__(s): super().__init__(); s.cues = []; s.scene_ins = []
    def handle_starttag(s, tag, a):
        a = dict(a); cls = set((a.get("class") or "").split())
        if "scene" in cls and "data-in" in a:
            s.scene_ins.append(float(a["data-in"]));
            if a.get("data-exit") == "cut": s.cues.append((float(a["data-out"]), "hit", 0))
            return
        if "type" in cls and "data-t" in a:
            d = float(a.get("data-dur", 0)) or .6; s.cues.append((float(a["data-t"]), "typing", max(.4, d)))
        if ("hlbox" in cls or tag == "mark") and "data-t" in a: s.cues.append((float(a["data-t"]), "highlight", 0))
        if "count" in cls and "data-t" in a: s.cues.append((float(a["data-t"]) + float(a.get("data-dur", 1.5)), "hit", 0))
        if "data-in" in a and tag not in ("video", "section"):
            anim, t = a.get("data-anim", "fade"), float(a["data-in"])
            if anim == "none" or anim == "fade": return
            if cls & TICK: s.cues.append((t, "tick", 0))
            elif anim in ("pop", "blur", "zoom") or (anim in ("rise", "drop", "slide") and cls & CARD): s.cues.append((t, "popup", 0))

def cues(page):
    p = P(); p.feed(open(page, encoding="utf-8").read())
    out = [(round(t - .15, 3), "whoosh", 0) for t in sorted(set(p.scene_ins)) if t > .05] + p.cues
    out.sort(); merged = []
    for t, r, d in out:
        if merged and merged[-1][1] == r and t - merged[-1][0] < .12: continue
        merged.append((max(0.0, t), r, d))
    return merged

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    page = sys.argv[1]; C = cues(page)
    J = [{"t": t, "role": r, "dur": d, "edits_sound": ROLES[r][0], "edits_id": ROLES[r][1], "volume": ROLES[r][2]} for t, r, d in C]
    json.dump(J, open(os.path.join(os.path.dirname(os.path.abspath(page)), "cues.json"), "w"), indent=1)
    for c in J: print(f'{c["t"]:7.2f}s  {c["role"]:<9} {c["edits_sound"]:<24} id {c["edits_id"]}  vol {c["volume"]}' + (f'  dur {c["dur"]:.2f}' if c["dur"] else ""))
    print(f"{len(J)} cues -> cues.json")
    if "--mix" in sys.argv:
        d = sys.argv[sys.argv.index("--mix") + 1]; out = sys.argv[sys.argv.index("--mix") + 2]
        files = {r: (glob.glob(os.path.join(d, r + ".*")) or [None])[0] for r in ROLES}
        missing = sorted({c["role"] for c in J if not files[c["role"]]})
        if missing: print("missing in", d, ":", ", ".join(m + ".mp3" for m in missing), "(those cues are skipped)")
        use = [c for c in J if files[c["role"]]]
        if not use: print("no sound files found; nothing mixed"); return
        args, fl = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"], []
        for i, c in enumerate(use):
            args += ["-i", files[c["role"]]]; ms = int(c["t"] * 1000)
            fo = max(0, c["dur"] - .15)
            trim = f"atrim=0:{c['dur']:.3f},afade=t=out:st={fo:.3f}:d=0.15," if c["dur"] else ""
            fl.append(f"[{i}:a]{trim}aformat=sample_rates=48000:channel_layouts=stereo,volume={c['volume']},adelay={ms}|{ms}[a{i}]")
        fl.append("".join(f"[a{i}]" for i in range(len(use))) + f"amix=inputs={len(use)}:normalize=0[out]")
        subprocess.run(args + ["-filter_complex", ";".join(fl), "-map", "[out]", "-c:a", "pcm_s16le", out], check=True)
        print("mixed", len(use), "cues ->", out)

if __name__ == "__main__": main()
