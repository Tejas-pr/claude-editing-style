#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""LOCAL cut (no Edits app): remove pauses, speed up, and get word times from a raw face-cam / voiceover recording.

  python3 -I local_cut.py RAW.mov OUTDIR [--speed 1.15] [--min-pause 0.3] [--margin 0.06] [--db -38]
                          [--model ggml-small.en.bin] [--cut 12.4-13.9 --cut 30-31.2]

Writes into OUTDIR:
  face-cut.mp4   the cut + sped-up recording (video + audio), timeline-aligned with the motion page (1440x2560 cover crop)
  map.json       {"keep": [[a, b, timeline_start], ...], "speed": s, "end": seconds}  (same format as Edits PLAN.map.json,
                 so reel_lib.load_map() / words() work unchanged)
  words.json     [[word, timeline_seconds], ...] if whisper.cpp (`whisper-cli`) and a model are available
                 (--model or $WHISPER_MODEL); otherwise transcribe however you like and time words yourself.
Needs ffmpeg. --cut removes extra ranges (retakes, blips) in RAW seconds.
"""
import json, os, re, shutil, subprocess, sys

def arg(k, d=None, many=False):
    a = sys.argv; out = [a[i + 1] for i, x in enumerate(a) if x == k and i + 1 < len(a)]
    return out if many else (out[0] if out else d)

if len(sys.argv) < 3: print(__doc__); sys.exit(1)
RAW, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
SP, MINP, MAR, DB = float(arg("--speed", 1.15)), float(arg("--min-pause", .3)), float(arg("--margin", .06)), arg("--db", "-38")
EXTRA = [tuple(map(float, c.split("-"))) for c in arg("--cut", many=True)]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", RAW], capture_output=True, text=True).stdout)

# 1) pauses
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", RAW, "-af", f"silencedetect=noise={DB}dB:d={MINP}", "-f", "null", "-"], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
gaps = [(a + MAR, b - MAR) for a, b in zip(st, en + [dur]) if b - a >= MINP] + EXTRA
gaps = sorted((max(0, a), min(dur, b)) for a, b in gaps if b > a)
keep, t = [], 0.0
for a, b in gaps:
    if a > t + .05: keep.append([round(t, 4), round(a, 4)])
    t = max(t, b)
if dur > t + .05: keep.append([round(t, 4), round(dur, 4)])
pos, K = 0.0, []
for a, b in keep: K.append([a, b, round(pos, 4)]); pos += (b - a) / SP
json.dump({"keep": K, "speed": SP, "end": round(pos, 3)}, open(os.path.join(OUT, "map.json"), "w"), indent=1)
print(f"kept {len(K)} pieces, {sum(b - a for a, b, _ in K):.1f}s of {dur:.1f}s raw -> {pos:.1f}s at {SP}x")

# 2) cut + speed (video and audio), cover-crop to the reel canvas
v = ";".join(f"[0:v]trim=start={a}:end={b},setpts=(PTS-STARTPTS)/{SP}[v{i}]" for i, (a, b, _) in enumerate(K))
au = ";".join(f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,atempo={SP},afade=t=in:d=0.01,afade=t=out:st={max(0, (b - a) / SP - .015):.4f}:d=0.015[a{i}]" for i, (a, b, _) in enumerate(K))
fc = f"{v};{au};" + "".join(f"[v{i}][a{i}]" for i in range(len(K))) + f"concat=n={len(K)}:v=1:a=1[vc][ac];[vc]fps=30,scale=1440:2560:force_original_aspect_ratio=increase,crop=1440:2560[vo]"
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", RAW, "-filter_complex", fc, "-map", "[vo]", "-map", "[ac]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-g", "15", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
                os.path.join(OUT, "face-cut.mp4")], check=True)
print("wrote", os.path.join(OUT, "face-cut.mp4"))

# 3) word times (whisper.cpp), mapped from raw time to timeline time
model, cli = arg("--model", os.environ.get("WHISPER_MODEL")), shutil.which("whisper-cli")
if cli and model and os.path.exists(model):
    wav = os.path.join(OUT, "raw16k.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", RAW, "-ar", "16000", "-ac", "1", wav], check=True)
    subprocess.run([cli, "-m", model, "-f", wav, "-ml", "1", "-oj", "-of", os.path.join(OUT, "whisper")], check=True, capture_output=True)
    J = json.load(open(os.path.join(OUT, "whisper.json")))
    def tl(t):
        for a, b, s in K:
            if a - .02 <= t <= b + .02: return s + (max(t, a) - a) / SP
        return None
    W = [[x["text"].strip(), round(tl(x["offsets"]["from"] / 1000), 3)] for x in J["transcription"] if x["text"].strip()]
    W = [w for w in W if w[1] is not None]
    M = []
    for w in W:   # whisper -ml 1 splits punctuation into its own token: glue it to the word before
        if M and all(not c.isalnum() for c in w[0]): M[-1][0] += w[0]
        else: M.append(w)
    W = M
    json.dump(W, open(os.path.join(OUT, "words.json"), "w")); os.remove(wav)
    print(f"words.json: {len(W)} words")
else:
    print("no whisper-cli/model: skipped words.json (set --model or $WHISPER_MODEL to a ggml model, e.g. ggml-small.en.bin)")
