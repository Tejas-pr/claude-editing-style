#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Canvas-sized overlay images for a 1440x2560 reel (needs ffmpeg; no drawtext needed).
Usage: python3 -I assets.py MODE SRC OUT [options]
  cover   SRC OUT W H [brightness=-0.06] [pos=(iw-ow)/2:(ih-oh)/2]   fill + crop + mild grade
  blurfit SRC OUT W H [k=0.94] [brightness=0]                          contain on blurred, darkened copy
  onsolid SRC OUT W H COLOR k                                          contain on solid colour (0xRRGGBB)
  shade   SRC OUT W H centre halfwidth peak global                     bake soft dark band for white text
  crop    SRC OUT w h x y                                              plain crop (e.g. from a 2x screenshot)
Sizes: top panel 1440x1280 (y .25), full 1440x2560, stacked panel 1440x853.
Shade examples: text near panel bottom -> centre 0.85 halfwidth 0.3 peak 0.7 global 0.05;
busy screenshot panel -> 0.5 0.5 0.45 0.25.
"""
import subprocess, sys
def ff(*a): subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)
m, src, out, *o = sys.argv[1:]
if m == "crop":
    w, h, x, y = o; ff("-i", src, "-vf", f"crop={w}:{h}:{x}:{y}", out); sys.exit()
W, H = int(o[0]), int(o[1])
if m == "cover":
    b = o[2] if len(o) > 2 else "-0.06"; pos = o[3] if len(o) > 3 else "(iw-ow)/2:(ih-oh)/2"
    ff("-i", src, "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}:{pos},setsar=1,"
       f"eq=brightness={b}:saturation=0.85:contrast=1.05", "-frames:v", "1", out)
elif m == "blurfit":
    k = float(o[2]) if len(o) > 2 else 0.94; b = o[3] if len(o) > 3 else "0"
    ff("-i", src, "-filter_complex", f"[0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,"
       f"eq=brightness=-0.35[bg];[0]scale={int(W*k)}:{int(H*k)}:force_original_aspect_ratio=decrease:flags=lanczos,"
       f"eq=brightness={b}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=rgb24", "-frames:v", "1", out)
elif m == "onsolid":
    color, k = o[2], float(o[3])
    ff("-f", "lavfi", "-i", f"color=c={color}:s={W}x{H}", "-i", src, "-filter_complex",
       f"[1]scale={int(W*k)}:{int(H*k)}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
       f"[0][fg]overlay=(W-w)/2:(H-h)/2:format=auto,format=rgb24", "-frames:v", "1", out)
elif m == "shade":
    c, w, p, g = o[2:6]
    a = f"255*min(1,{g}+{p}*max(0,1-abs(Y/{H}-{c})/{w}))"
    ff("-i", src, "-f", "lavfi", "-i", f"color=c=black:s={W}x{H},format=rgba,geq=r=0:g=0:b=0:a='{a}'",
       "-filter_complex", "[0][1]overlay=0:0:format=auto,format=rgb24", "-frames:v", "1", out)
