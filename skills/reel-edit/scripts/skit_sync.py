#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""style-06 Skit: time a re-acted take to a trending sound (lip-sync meme / funny skit). Pure Python + ffmpeg, no numpy.

  python3 skit_sync.py levels SOUND [--from 4 --to 11]            20 ms loudness map + hit list (beats, claps, words)
  python3 skit_sync.py motion TAKE  [--from 5 --to 8 --box x,y,w,h] motion per frame in a box (hands, mouth) + peaks
  python3 skit_sync.py plan   skit.json                           piece-by-piece speeds from anchor pairs (+ Edits steps)
  python3 skit_sync.py render skit.json OUT.mp4                   local cut: pieces + close-ups + kept sound (no text)

Why: the take is the actors' own voices, so waveform sync is impossible and one offset never fits. Match MOMENTS
instead: words (transcribe both, or Edits transcribeClip), beat hits (levels), hand/mouth hits (motion). Each pair
(take time -> sound time) is an anchor; the pieces between anchors get their own speed.

skit.json (times in seconds; "ref" = time in the ORIGINAL sound file):
{
  "take": "take.mov", "sound": "sound.mp3", "fps": 30, "w": 1440, "h": 2560,
  "sound_keep": [[0, 9.38], [10.37, 14.55]],       # optional: cut quiet gaps out of the sound (default: all of it)
  "anchors": [[0, 0, "start"], [2.008, 2.24, "founder"], [2.333, 2.6, "cut to close-ups"],
              [3.433, 3.733, "back to wide"], [4.3, 4.6, "her line"], [5.3, 6.0, "RPS hit 1"],
              [6.25, 7.2, "reveal"], [9.144, 11.944, "I'm"], [11.1, 14.55, "end"]],
  "still": [[6.25, 7.2]],                          # take ranges where nothing moves: slow-mo there is invisible
  "closeups": [{"ref": 2.6, "src": 3.0,            # punch-in shots that replace the wide shot from ref 2.6
                "shots": [[0.333, 0.52, 0.27], [0.3, 0.10, 0.36], [0.234, 0.52, 0.27], [0.266, 0.10, 0.36]],
                "scale": 2.0}]                     # each shot: [duration, face x, face y] in the raw frame (0..1)
}
Speeds outside 0.7..1.3 are flagged (outside a "still" range): fix them with another anchor, a still hold, or a
sound cut in a quiet gap (levels shows where). Text/emoji overlays are added in Edits (or your editor) afterwards.
"""
import json, math, os, re, subprocess, sys, array

LO, HI = 0.7, 1.3


def _pcm(path, start, dur, sr=8000):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"]
    a = array.array("h"); a.frombytes(subprocess.run(cmd, capture_output=True, check=True).stdout); return a


def levels(path, t0=0.0, t1=None, hop=0.02):
    t1 = t1 if t1 is not None else _duration(path)
    a = _pcm(path, t0, t1 - t0); n = int(8000 * hop); out = []
    for k, i in enumerate(range(0, len(a) - n, n)):
        s = sum(x * x for x in a[i:i + n]) / n
        out.append((round(t0 + k * hop, 3), round(10 * math.log10(s / 32768 ** 2 + 1e-12), 1)))
    return out


def hits(lv, jump=7.0, floor=-25.0, gap=0.15):
    """onsets: level rises >= jump dB within 60 ms and lands above floor; one per gap seconds."""
    res, last = [], -9
    for i in range(3, len(lv)):
        t, v = lv[i]
        if v > floor and v - min(x[1] for x in lv[i - 3:i]) >= jump and t - last >= gap:
            res.append((t, v)); last = t
    return res


def motion(path, t0, t1, box=(0.25, 0.42, 0.5, 0.26)):
    x, y, w, h = box
    vf = (f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},scale=96:-2,format=gray,tblend=all_mode=difference,"
          f"signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-")
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", path, "-vf", vf, "-an", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    out, t = [], None
    for line in r.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", line)
        if m: t = float(m.group(1))
        m = re.search(r"YAVG=([\d.]+)", line)
        if m and t is not None: out.append((round(t0 + t, 3), float(m.group(1))))
    return out


def peaks(series, min_gap=0.1):
    res = []
    for i in range(1, len(series) - 1):
        t, v = series[i]
        if v >= series[i - 1][1] and v > series[i + 1][1] and v > 1.0 and (not res or t - res[-1][0] >= min_gap):
            res.append((t, v))
    return res


def _duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return float(r.stdout.strip())


def ref_to_tl(ref, keep):
    """original-sound time -> timeline time after sound_keep cuts (None if it falls in a cut)."""
    tl = 0.0
    for a, b in keep:
        if a <= ref <= b: return round(tl + ref - a, 4)
        tl += b - a
    return None


def plan(P):
    keep = P.get("sound_keep") or [[0, _duration(P["sound"])]]
    A = [(s, ref_to_tl(r, keep), (n[0] if n else "")) for s, r, *n in P["anchors"]]
    if any(t is None for _, t, _ in A): raise SystemExit("an anchor's ref time falls inside a sound cut")
    cu, win = [], []
    for c in P.get("closeups", []):
        t = ref_to_tl(c["ref"], keep); s = c["src"]; t_start = t
        for d, fx, fy in c["shots"]:
            cu.append({"kind": "closeup", "src_in": s, "src_out": s + d, "speed": 1.0, "tl_in": t, "tl_out": t + d,
                       "face": [fx, fy], "scale": c.get("scale", 2.0)}); t += d; s += d
        win.append((t_start, t))
    still = P.get("still", [])
    pieces = []
    for (s0, t0, n0), (s1, t1, n1) in zip(A, A[1:]):
        if t1 <= t0 or s1 <= s0: raise SystemExit(f"anchors must increase: {n0} -> {n1}")
        if any(a - 1e-6 <= t0 and t1 <= b + 1e-6 for a, b in win): continue          # covered by close-ups
        sp = (s1 - s0) / (t1 - t0)
        is_still = any(a - 0.02 <= s0 and s1 <= b + 0.02 for a, b in still)
        flag = "" if LO <= sp <= HI else ("ok (still hold)" if is_still else "CHECK: add an anchor, a still hold or a sound cut")
        pieces.append({"kind": "wide", "src_in": s0, "src_out": s1, "speed": round(sp, 4), "tl_in": t0, "tl_out": t1,
                       "label": f"{n0} -> {n1}", "flag": flag})
    out = sorted(pieces + cu, key=lambda p: p["tl_in"])
    for a, b in zip(out, out[1:]):
        if abs(a["tl_out"] - b["tl_in"]) > 0.02:
            print(f"! gap/overlap at {a['tl_out']:.3f} -> {b['tl_in']:.3f}: add an anchor at the close-up edges", file=sys.stderr)
    return out, keep


def crop_for(fx, fy, s, W, H):
    """close-up window: face at 35% from the top, clamped inside the frame. Returns ffmpeg crop args (pixels)."""
    w, h = 1 / s, 1 / s
    cx = min(max(fx, w / 2), 1 - w / 2); cy = min(max(fy + 0.15 / s, h / 2), 1 - h / 2)
    return f"crop=iw*{w:.4f}:ih*{h:.4f}:iw*{cx - w / 2:.4f}:ih*{cy - h / 2:.4f}"


def render(P, out_path):
    pieces, keep = plan(P)
    W, H, fps = P.get("w", 1440), P.get("h", 2560), P.get("fps", 30)
    fit = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps}"
    fc = []
    for i, p in enumerate(pieces):
        crop = (crop_for(*p["face"], p["scale"], W, H) + ",") if p["kind"] == "closeup" else ""
        fc.append(f"[0:v]trim=start={p['src_in']:.4f}:end={p['src_out']:.4f},setpts=(PTS-STARTPTS)/{p['speed']},{crop}{fit}[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=1:a=0[vout]")
    for j, (a, b) in enumerate(keep):
        fc.append(f"[1:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, b - a - 0.01):.3f}:d=0.01[a{j}]")
    fc.append("".join(f"[a{j}]" for j in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[aout]")
    end = pieces[-1]["tl_out"]
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", P["take"], "-i", P["sound"], "-filter_complex", ";".join(fc),
           "-map", "[vout]", "-map", "[aout]", "-t", f"{end:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out_path]
    subprocess.run(cmd, check=True)
    print(f"{out_path}  ({end:.2f} s). Next: overlays (title, emoji) in your editor, then finish-export.sh for -14 LUFS.")


def _args(argv, key, default=None, cast=float):
    return cast(argv[argv.index(key) + 1]) if key in argv else default


if __name__ == "__main__":
    av = sys.argv[1:]
    if not av or av[0] not in ("levels", "motion", "plan", "render"): print(__doc__); sys.exit(1)
    cmd = av[0]
    if cmd == "levels":
        lv = levels(av[1], _args(av, "--from", 0.0), _args(av, "--to", None))
        for i in range(0, len(lv), 12): print("  ".join(f"{t:.2f}:{v:.0f}" for t, v in lv[i:i + 12]))
        print("hits:", ", ".join(f"{t:.2f}" for t, _ in hits(lv)))
    elif cmd == "motion":
        box = tuple(float(x) for x in _args(av, "--box", "0.25,0.42,0.5,0.26", str).split(","))
        m = motion(av[1], _args(av, "--from", 0.0), _args(av, "--to", 3.0), box)
        print("  ".join(f"{t:.2f}:{v:.1f}" for t, v in m)); print("peaks:", ", ".join(f"{t:.2f}" for t, _ in peaks(m)))
        print("still (motion < 1):", ", ".join(f"{t:.2f}" for t, v in m if v < 1.0)[:400])
    elif cmd == "plan":
        P = json.load(open(av[1])); pieces, keep = plan(P)
        print(f"{'kind':8} {'take in-out':>14} {'speed':>7} {'timeline':>16}  note")
        for p in pieces:
            note = p.get("label", f"face {p.get('face')} x{p.get('scale')}") + ("  " + p.get("flag", "") if p.get("flag") else "")
            print(f"{p['kind']:8} {p['src_in']:6.3f}-{p['src_out']:6.3f} {p['speed']:7.3f} {p['tl_in']:7.3f}-{p['tl_out']:7.3f}  {note}")
        print("sound pieces (original s -> timeline s):", ", ".join(f"{a}-{b} @ {ref_to_tl(a, keep)}" for a, b in keep))
        print("Edits: splitAt the take at every take in/out, delete unused, setSpeed per piece, setTransform close-ups "
              "(scale, x = 0.5 + (0.5 - fx)*scale, y = 0.5 + (0.5 - (fy + 0.15/scale))*scale, keyframes 'clear'), "
              "setVolume 0 on the take, sound on its own track split at sound_keep and butt-joined.")
    else:
        render(json.load(open(av[1])), av[2])
