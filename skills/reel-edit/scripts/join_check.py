#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Check that every kept piece starts and ends in silence.
Usage: python3 -I join_check.py SOURCE.mp4 'in1,out1 in2,out2 ...'   (source seconds, from `clips`)
Anything louder than about -45 dB at an edge clips a word: move that edge 0.02-0.05 s.
"""
import array, math, subprocess, sys
pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", sys.argv[1], "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
a = array.array("h", pcm); sr = 16000
def db(t0, t1):
    s = a[int(t0*sr):int(t1*sr)]
    return -99 if not s else 20*math.log10(math.sqrt(sum(x*x for x in s)/len(s))/32768 + 1e-9)
for i, pair in enumerate(sys.argv[2].split()):
    s, e = map(float, pair.split(","))
    a0, a1 = db(s, s+0.04), db(e-0.04, e)
    flag = "  <-- fix" if max(a0, a1) > -45 else ""
    print(f"{i:2d} in {s:7.2f} {a0:6.1f} dB | out {e:7.2f} {a1:6.1f} dB{flag}")
