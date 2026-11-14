#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Plan a pause cut for a voiceover or talking track in Edits, then the moves that close the gaps.

1) plan:     python3 -I cut_plan.py plan PLAN.json
   PLAN.json = {"speed":1.25, "min_pause":0.3, "margin":0.06,
                "elements":[{"id":"<element id>", "start":0, "end":42.6,
                             "pauses":[[0,1.01],[3.56,4.08],...],      # findPauses result (timeline s)
                             "cut":[[27.39,28.38]]}]}                 # optional extra ranges to remove (retakes, blips)
   Prints splitAt times per element and the gap ranges to delete. Writes PLAN.cuts.json.
2) classify: python3 -I cut_plan.py classify PLAN.cuts.json PIECES.json
   PIECES.json = the "pieces" arrays from every splitAt result, concatenated. Prints the ids to delete (gaps) and to keep.
3) moves:    python3 -I cut_plan.py moves PLAN.cuts.json ELEMENTS.json
   ELEMENTS.json = `elements` result AFTER setSpeed on the kept pieces (fields id,startTime,duration).
   Prints move targets in order (butt-joined from 0) and writes PLAN.map.json = {"keep":[[a,b,new_start],...],"speed":S,"end":E}
   which reel_lib.load_map() uses to map transcript word times onto the finished timeline.
"""
import json, sys

def plan(path):
    P = json.load(open(path)); m, mn = P.get("margin", .06), P.get("min_pause", .3)
    gaps_all, out = [], {"speed": P.get("speed", 1.25), "elements": []}
    for el in P["elements"]:
        s0, e0 = el["start"], el["end"]; gaps = []
        for a, b in el.get("pauses", []):
            if b - a < mn: continue
            ga = s0 if a <= s0 + .01 else a + m          # lead silence: cut from the very start
            gb = e0 if b >= e0 - .01 else b - m          # tail silence: cut to the very end
            if gb - ga > .05: gaps.append([round(ga, 3), round(gb, 3)])
        gaps += [[round(a, 3), round(b, 3)] for a, b in el.get("cut", [])]
        gaps.sort(); merged = []
        for g in gaps:
            if merged and g[0] <= merged[-1][1] + .02: merged[-1][1] = max(merged[-1][1], g[1])
            else: merged.append(g)
        times = sorted({t for g in merged for t in g if s0 + .01 < t < e0 - .01})
        keep, cur = [], s0
        for a, b in merged:
            if a > cur + .01: keep.append([round(cur, 3), a])
            cur = max(cur, b)
        if cur < e0 - .01: keep.append([round(cur, 3), e0])
        print(f"{el['id']}: splitAt {json.dumps(times)}")
        print(f"   delete {len(merged)} gaps ({sum(b-a for a,b in merged):.2f}s), keep {len(keep)} pieces ({sum(b-a for a,b in keep):.2f}s)")
        out["elements"].append({"id": el["id"], "gaps": merged, "keep": keep})
    total = sum(b - a for e in out["elements"] for a, b in e["keep"])
    print(f"kept {total:.2f}s -> {total/out['speed']:.2f}s at {out['speed']}x")
    json.dump(out, open(path.replace(".json", "") + ".cuts.json", "w"), indent=1)

def classify(cuts, pieces):
    C = json.load(open(cuts)); P = json.load(open(pieces)); gaps = [g for e in C["elements"] for g in e["gaps"]]
    dele, keep = [], []
    for p in P:
        mid = (p["start"] + p["end"]) / 2
        (dele if any(a - .005 <= mid <= b + .005 for a, b in gaps) else keep).append(p)
    print("DELETE", len(dele), json.dumps([p["id"] for p in dele]))
    print("KEEP  ", len(keep), json.dumps([p["id"] for p in sorted(keep, key=lambda p: p["start"])]))

def moves(cuts, elements):
    C = json.load(open(cuts)); E = json.load(open(elements)); E = E.get("elements", E)
    keep = sorted([k for e in C["elements"] for k in e["keep"]]); E = sorted(E, key=lambda e: e["startTime"])
    if len(E) != len(keep): print(f"warning: {len(E)} elements but {len(keep)} kept ranges (contiguous pieces may have been split twice)")
    t, out = 0.0, []
    for e in E:
        print(f"move {e['id']} toSeconds {t:.4f}"); out.append((e["id"], round(t, 4))); t += e["duration"]
    # map original ranges -> new starts (uses the planned keep ranges; pieces split by the app at a source boundary share a range)
    starts, t = [], 0.0
    for a, b in keep: starts.append([a, b, round(t, 4)]); t += (b - a) / C["speed"]
    json.dump({"keep": starts, "speed": C["speed"], "end": round(t, 3)}, open(cuts.replace(".cuts.json", "") + ".map.json", "w"), indent=1)
    print(f"end {t:.2f}s")

if __name__ == "__main__":
    cmd = sys.argv[1]
    {"plan": lambda: plan(sys.argv[2]), "classify": lambda: classify(sys.argv[2], sys.argv[3]), "moves": lambda: moves(sys.argv[2], sys.argv[3])}[cmd]()
