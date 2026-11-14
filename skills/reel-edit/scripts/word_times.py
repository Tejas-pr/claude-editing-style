#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Edits `captions` gives segment start/end + tokens, not per-word times. This spreads each segment's
duration over its words by length (good to about 0.1 s) and prints data-words strings for paper.html.
  python3 -I word_times.py captions.json      (the JSON result of the Edits `captions` call)
"""
import json, sys
d = json.load(open(sys.argv[1])); caps = d.get("captions", d)
for c in caps:
    a, b = c["startTime"], c["endTime"]; w = [t["text"] for t in c.get("tokens", [])] or c["text"].split()
    L = [len(x) + 2 for x in w]; tot = sum(L); acc = 0; out = []
    for x, l in zip(w, L): out.append(f"{a + (b - a) * acc / tot:.2f} {x}"); acc += l
    print("|".join(out))
