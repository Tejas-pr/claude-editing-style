# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# Generates motion.html for the no-voiceover outage reel: word times are paced for reading, not speech.
import sys, html
tpl, out = sys.argv[1], sys.argv[2]
def words(s, start, step):
    ws = s.split(); return "|".join(f"{start+i*step:.2f} {html.escape(w)}" for i, w in enumerate(ws)), start + len(ws)*step
def head(s, l1, l2):
    a, t = words(l1, s+0.15, 0.2); b, t2 = words(l2, t+0.15, 0.26)
    return f'  <p class="l1" data-words="{a}"></p>\n  <p class="l2" data-words="{b}"></p>\n', t2
P = []
# 1 hook
s, e = 0, 3.4; h, t = head(s, "Right now,", "Claude & Microsoft are down")
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="row" style="gap:6rem">
    <div class="col" data-in="{s-0.6}" data-anim="pop"><div class="card logo"><img src="claude-symbol.png"></div><span class="pill">Claude</span></div>
    <div class="col" data-in="{s-0.6}" data-anim="pop"><div class="card logo"><img src="mslogo.svg"></div><span class="pill">Microsoft 365</span></div>
  </div>
  <span class="pill live" data-in="{t+0.1:.2f}" data-anim="pop">● LIVE · Nov 13, 2026</span>
</section>''')
# 2 claude status
s, e = 3.4, 7.4; h, t = head(s, "Claude users can't", "even log in")
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="card wide shot" data-in="{s+0.1}" data-anim="rise"><img src="status-claude.png"></div>
  <div class="row"><span class="pill bad" data-in="{t+0.1:.2f}" data-anim="pop">claude.ai · major outage</span><span class="pill" data-in="{t+0.5:.2f}" data-anim="pop">Claude Code · partial</span></div>
</section>''')
# 3 microsoft apps
s, e = 7.4, 11.0; h, t = head(s, "Microsoft is down for", "a second day")
cols = "".join(f'''    <div class="col" data-in="{s+0.5+i*0.35:.2f}" data-anim="rise"><div class="card third app"><img src="{f}.svg"></div><span class="pill{' rust' if i==0 else ''}">{n}</span></div>\n''' for i,(f,n) in enumerate([("outlook","Outlook"),("teams","Teams"),("onedrive","OneDrive")]))
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="row" style="gap:2.6rem;align-items:flex-start">
{cols}  </div>
</section>''')
# 4 130,000 reports
s, e = 11.0, 14.6; h, t = head(s, "Outlook problem reports at the peak:", "")
a, t = words("Outlook problem reports at the peak:", s+0.15, 0.2)
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
  <p class="l1" data-words="{a}"></p>
  <div class="big" data-in="{t:.2f}" data-anim="fade" style="font-size:20rem"><span class="count" data-t="{t:.2f}" data-dur="1.4" data-from="0" data-to="130000"></span>+</div>
  <p class="src" data-in="{t+0.6:.2f}" data-anim="fade">Downdetector, Thursday peak · reported by AP</p>
  <span class="pill bad" data-in="{t+1.2:.2f}" data-anim="pop">Microsoft: the fix is "not taking as expected"</span>
</section>''')
# 5 who got hit
s, e = 14.6, 18.4; h, t = head(s, "It even hit", "governments & airlines")
items = ["Singapore government","Philippines government","Japan government","IndiGo airline","Parts of the UK's NHS"]
pills = "".join(f'    <span class="pill{" rust" if i==3 else ""}" data-in="{t+0.05+i*0.3:.2f}" data-anim="pop">{n}</span>\n' for i,n in enumerate(items))
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="stack">
{pills}  </div>
</section>''')
# 6 claude's outlook tools
s, e = 18.4, 22.0; h, t = head(s, "And Claude's Outlook tools?", "Broken by Microsoft")
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="card wide shot" data-in="{s+0.1}" data-anim="rise" style="height:46rem"><img src="status-m365.png"></div>
  <div class="quote" data-in="{t+0.05:.2f}" data-anim="rise">Anthropic: "caused by a <mark data-t="{t+0.4:.2f}">Microsoft 365 service incident</mark>"</div>
  <span class="pill" data-in="{t+1.0:.2f}" data-anim="pop">Login outage: cause not announced yet</span>
</section>''')
# 7 CTA
s, e = 22.0, 26.5; h, t = head(s, "Is Claude working for you?", "Comment UP or DOWN")
P.append(f'''<section class="scene" data-in="{s}" data-out="{e}">
{h}  <div class="row" style="gap:4rem"><span class="pill good big-pill" data-in="{t:.2f}" data-anim="pop">UP</span><span class="pill bad big-pill" data-in="{t+0.25:.2f}" data-anim="pop">DOWN</span></div>
  <span class="pill rust" data-in="{t+0.7:.2f}" data-anim="pop">Follow for live AI news</span>
</section>''')
src = open(tpl).read()
css = '''.card.logo{width:36rem;height:36rem;display:grid;place-items:center}.card.logo img{width:60%;height:60%;object-fit:contain}
.card.app{display:grid;place-items:center}.card.app img{width:62%;height:auto;object-fit:contain}
.card.shot img{object-fit:cover;object-position:50% 0}
.pill.live{border-color:var(--red);color:#fff;background:var(--red);font-weight:600}
.pill.bad{border-color:var(--red);color:var(--red)}.pill.good{border-color:var(--green);color:var(--green)}
.big-pill{font-size:7rem;padding:2rem 6rem;border-width:.4rem;font-weight:700}
.stack{display:flex;flex-direction:column;align-items:center;gap:2.6rem}.stack .pill{font-size:5rem;padding:1.8rem 4rem}
.scene > .l1:first-child + .big{margin-top:auto}
'''
src = src.replace('</style>', css + '</style>', 1)
a = src.index('<!-- ============================ SCENES'); b = src.index('<!-- ============================ END SCENES')
src = src[:a] + '<!-- ============================ SCENES -->\n' + "\n\n".join(P) + '\n' + src[b:]
src = src.replace('<title>Reel motion</title>', '<title>Claude Microsoft outage</title>')
open(out, 'w').write(src)
