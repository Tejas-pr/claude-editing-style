# Worked example: style-04 with a moving face card (14.6 s)

The sample reel (git reflog) used in `styles/style-04.png`. Run from a reel folder that holds `doc-reflog.png` (made with `scripts/source_shot.mjs`) and `face.mp4`.

```python
# style-04 SAMPLE (striver paper + smooth motion + moving face card), ~14.6 s. Silent motion; face = placeholder footage.
#   python3 -I build.py && node $SK/scripts/render.mjs motion.html motion.mov --alpha   (prints the face-window changes)
import sys, os
SK = os.environ.get("REEL_EDIT_SKILL", "<plugin>/skills/reel-edit"); sys.path.insert(0, SK + "/scripts"); from reel_lib import *
HERE = os.path.dirname(os.path.abspath(__file__))
def H(l1, l2=None): return f'<p class="l1" data-words="{l1}"></p>' + (f'<p class="l2" data-words="{l2}"></p>' if l2 else '')
def SUB(w): return f'<div class="sub" data-words="{w}"></div>'
FACE = ('<div class="facecard" data-show="0-2.7 bottom polaroid|2.7-4.9 top wide|4.9-7.4 bottom polaroid|'
        '10.4-12.7 full|12.7-14.6 bottom polaroid"><div class="hole"></div></div>')
A = ('<section class="scene" data-in="0" data-out="2.7">'
     + H("0 I|0 ran|0 git|0 reset|0 --hard|0 and", "0 lost*|0.9 two|1.1 days|1.35 of|1.5 commits.")
     + '<span class="datepill" data-in="1.6" data-anim="pop">git reset --hard HEAD~5</span></section>')
B = ('<section class="scene" data-in="2.7" data-out="4.9">'
     '<div class="roll serif" data-in="3.4" data-anim="blur" data-ts="4.1,4.5" style="font-size:11rem;height:3.4em">'
     '<span>gone?</span><span>deleted?</span><span style="color:#2f8a4f">safe.</span></div>'
     + SUB("2.75 Or|2.9 so|3.0 I|3.1 thought.*|3.5 My|3.62 commits|3.85 were...") + '</section>')
C = ('<section class="scene" data-in="4.9" data-out="7.4">'
     + H("4.95 Git|5.1 keeps|5.3 a|5.4 secret|5.7 diary:", "6.0 git|6.3 reflog*")
     + '<div class="code" data-in="5.0" data-anim="blur">'
       '<div><span class="k">$</span> <span class="type" data-t="6.0" data-dur=".5">git reflog</span></div>'
       '<div data-in="6.6" data-anim="fade"><span class="c">a1b2c3d</span> HEAD@{0}: reset: HEAD~5</div>'
       '<div data-in="6.7" data-anim="fade"><mark data-t="7.0"><span class="c">9f8e7d6</span> HEAD@{1}: commit: payments done</mark></div>'
       '</div></section>')
D = ('<section class="scene" data-in="7.4" data-out="10.4" data-cam="8.6 1.25 65 52">'
     + H("7.45 Lost|7.7 commits|7.95 stay|8.1 there|8.3 for", "8.5 30*|8.85 days.")
     + '<div class="shotcard lg" data-in="7.5" data-anim="blur"><img src="doc-reflog.png" alt="">'
       '<i class="hlbox" data-t="8.55" style="left:54.6%;top:34.7%;width:24.6%;height:12.9%"></i></div>'
       '<span class="srcline" data-in="7.9" data-anim="fade">git-scm.com · git config docs · gc.reflogExpireUnreachable</span></section>')
E = ('<section class="scene" data-in="10.4" data-out="12.7">' + SUB("10.45 Find|10.65 it,|10.9 then|11.1 reset*|11.4 back.") + '</section>')
F = ('<section class="scene" data-in="12.7" data-out="14.6">'
     + H("12.75 Send|12.95 this|13.1 to|13.2 the|13.3 dev|13.5 who|13.65 thinks|13.85 it's", "14.0 lost.*")
     + '<span class="bubble" data-in="12.8" data-anim="pop">wait, that\'s me</span></section>')
css = ":root{--kwc:#c62820}.code{font-size:3.6rem;width:86rem}"
assemble(template("style-04"), os.path.join(HERE, "motion.html"), scenes=[A, B, C, D, E, F, FACE], css=css,
         page_title="git reflog style-04 sample", captions="pop-serif")
print("ok")
```

Then either `node scripts/render.mjs motion.html motion.mov --alpha` (Edits) or `zsh scripts/local_render.sh motion.html face-cut.mp4 final.mp4` (local).

---
Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
