# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
# Pages timed to the creator's own voiceover (cut + 1.2x in Edits). Word times come from transcribeClip (source s),
# mapped through the kept segments: t_new = start_k + (t - a_k) / speed.
import sys, html, json
tpl, out, mapf = sys.argv[1:4]
M = json.load(open(mapf)); KEEP, ST, SP = M["keep"], M["starts"], M["speed"]
def tl(t):
    for (a, b), s in zip(KEEP, ST):
        if a - 0.02 <= t <= b + 0.02: return s + (max(t, a) - a) / SP
    best = min(range(len(KEEP)), key=lambda k: min(abs(t-KEEP[k][0]), abs(t-KEEP[k][1])))
    a, b = KEEP[best]; return ST[best] + (min(max(t, a), b) - a) / SP
RAW = [("Claude",1.04),("is",1.36),("down,",1.5),("Microsoft",1.9),("is",2.46),("down.",2.64),("On",3.26),("the",3.44),("same",3.56),("day.",3.82),
("Right",4.36),("now,",4.66),("Claude",4.96),("users",5.32),("can't",5.66),("even",5.94),("log",6.32),("in.",6.58),
("And",7.4),("Microsoft?",7.58),("Outlook,",8.62),("Teams,",9.38),("OneDrive,",10.0),("broke",10.88),("down",11.14),("for",11.4),("a",11.64),("second",11.7),("day.",12.04),
("Over",12.76),("130,000",13.08),("people",14.0),("reported",14.3),("Outlook",14.84),("problems,",15.36),("and",16.12),("Microsoft",16.28),("admits",16.82),("the",17.24),("fix",17.36),("is",17.78),("not",18.0),("taking",18.4),("as",18.76),("expected.",18.94),
("It's",20.76),("hitting",20.98),("governments,",21.34),("airlines,",22.54),("even",23.58),("UK's",24.0),("NHS.",24.34),
("Here's",25.5),("the",25.72),("twist:",25.84),("Claude's",26.52),("Outlook",26.98),("tools",27.62),("broke",28.02),("because",29.06),("of",29.44),("Microsoft.",29.58),
("But",30.88),("the",31.12),("login",31.26),("outage?",31.62),("Still",32.26),("no",32.56),("cause.",32.72),
("So,",33.38),("is",34.5),("Claude",34.52),("working",34.9),("for",35.18),("you?",35.38),("Comment",35.68),("up",36.16),("or",36.7),("down.",36.88)]
W = [(w, tl(t)) for w, t in RAW]
END = round(tl(37.3) + 0.9, 2)
def span(a, b): return "|".join(f"{W[i][1]:.2f} {html.escape(W[i][0])}" for i in range(a, b + 1))
def t(i): return W[i][1]
B = [0, 10, 18, 29, 45, 52, 62, 69]   # first word index of each page
def pin(k): return 0 if k == 0 else round(t(B[k]) - 0.12, 2)
def pout(k): return END if k + 1 == len(B) else pin(k + 1)
P = []
P.append(f'''<section class="scene" data-in="0" data-out="{pout(0)}">
  <p class="l1" data-words="{span(0,5)}"></p>
  <p class="l2" data-words="{span(6,9)}"></p>
  <div class="row" style="gap:6rem">
    <div class="col" data-in="-0.6" data-anim="pop"><div class="card logo"><img src="claude-symbol.png"></div><span class="pill">Claude</span></div>
    <div class="col" data-in="{t(3):.2f}" data-anim="pop"><div class="card logo"><img src="mslogo.svg"></div><span class="pill">Microsoft 365</span></div>
  </div>
  <span class="pill live" data-in="{t(8):.2f}" data-anim="pop">● LIVE · Nov 13, 2026</span>
</section>''')
P.append(f'''<section class="scene" data-in="{pin(1)}" data-out="{pout(1)}">
  <p class="l1" data-words="{span(10,13)}"></p>
  <p class="l2" data-words="{span(14,17)}"></p>
  <div class="card wide shot" data-in="{pin(1)+0.05:.2f}" data-anim="rise"><img src="status-claude.png"></div>
  <div class="row"><span class="pill bad" data-in="{t(16):.2f}" data-anim="pop">claude.ai · major outage</span><span class="pill" data-in="{t(17)+0.2:.2f}" data-anim="pop">Claude Code · partial</span></div>
</section>''')
cols = "".join(f'''    <div class="col" data-in="{t(20+i):.2f}" data-anim="rise"><div class="card third app"><img src="{f}.svg"></div><span class="pill{' rust' if i==0 else ''}">{n}</span></div>\n''' for i,(f,n) in enumerate([("outlook","Outlook"),("teams","Teams"),("onedrive","OneDrive")]))
P.append(f'''<section class="scene" data-in="{pin(2)}" data-out="{pout(2)}">
  <p class="l1" data-words="{span(18,19)}"></p>
  <p class="l2" data-words="{span(23,28)}"></p>
  <div class="row" style="gap:2.6rem;align-items:flex-start">
{cols}  </div>
</section>''')
P.append(f'''<section class="scene" data-in="{pin(3)}" data-out="{pout(3)}">
  <p class="l1" data-words="{span(31,34)}"></p>
  <div class="big" data-in="{t(30)-0.1:.2f}" data-anim="fade" style="font-size:20rem"><span class="count" data-t="{t(30)-0.1:.2f}" data-dur="1.0" data-from="0" data-to="130000"></span>+</div>
  <p class="src" data-in="{t(33):.2f}" data-anim="fade">Downdetector, Thursday peak · reported by AP</p>
  <div class="quote" data-in="{t(36):.2f}" data-anim="rise">Microsoft admits the fix is <mark data-t="{t(41):.2f}">"not taking as expected"</mark></div>
</section>''')
gov = ["Singapore government","Philippines government","Japan government"]
pills = "".join(f'    <span class="pill" data-in="{t(47)+i*0.2:.2f}" data-anim="pop">{n}</span>\n' for i,n in enumerate(gov))
pills += f'    <span class="pill rust" data-in="{t(48):.2f}" data-anim="pop">IndiGo airline</span>\n'
pills += f'    <span class="pill" data-in="{t(50):.2f}" data-anim="pop">Parts of the UK\'s NHS</span>\n'
P.append(f'''<section class="scene" data-in="{pin(4)}" data-out="{pout(4)}">
  <p class="l1" data-words="{span(45,46)}"></p>
  <p class="l2" data-words="{span(47,48)}"></p>
  <div class="stack">
{pills}  </div>
</section>''')
P.append(f'''<section class="scene" data-in="{pin(5)}" data-out="{pout(5)}">
  <p class="l1" data-words="{span(52,57)}"></p>
  <p class="l2" data-words="{span(58,61)}"></p>
  <div class="card wide shot" data-in="{pin(5)+0.05:.2f}" data-anim="rise" style="height:46rem"><img src="status-m365.png"></div>
  <div class="quote" data-in="{t(58):.2f}" data-anim="rise">Anthropic: "caused by a <mark data-t="{t(61):.2f}">Microsoft 365 service incident</mark>"</div>
</section>''')
P.append(f'''<section class="scene" data-in="{pin(6)}" data-out="{pout(6)}">
  <p class="l1" data-words="{span(62,65)}"></p>
  <p class="l2" data-words="{span(66,68)}"></p>
  <div class="quote" data-in="{pin(6)+0.1:.2f}" data-anim="rise">Claude status, 09:58 UTC: "We are <mark data-t="{t(66):.2f}">investigating</mark> an issue with users authenticating to Claude.ai and Claude Code."</div>
  <span class="pill" data-in="{t(68)+0.15:.2f}" data-anim="pop">No cause announced yet</span>
</section>''')
P.append(f'''<section class="scene" data-in="{pin(7)}" data-out="{END}">
  <p class="l1" data-words="{span(69,74)}"></p>
  <p class="l2" data-words="{span(75,78)}"></p>
  <div class="row" style="gap:4rem"><span class="pill good big-pill" data-in="{t(76):.2f}" data-anim="pop">UP</span><span class="pill bad big-pill" data-in="{t(78):.2f}" data-anim="pop">DOWN</span></div>
  <span class="pill rust" data-in="{t(78)+0.5:.2f}" data-anim="pop">Follow for live AI news</span>
</section>''')
src = open(tpl).read()
css = open(sys.argv[4]).read() if len(sys.argv) > 4 else ''
a = src.index('<!-- ============================ SCENES'); b = src.index('<!-- ============================ END SCENES')
src = src[:a] + '<!-- ============================ SCENES -->\n' + "\n\n".join(P) + '\n' + src[b:]
src = src.replace('</style>', css + '</style>', 1).replace('<title>Reel motion</title>', '<title>Claude Microsoft outage</title>')
open(out, 'w').write(src)
print(json.dumps({"END": END, "pages": [pin(k) for k in range(len(B))], "key": {"down": round(t(2),2), "count": round(t(30),2), "gov": round(t(47),2), "airline": round(t(48),2), "twist": round(t(54),2), "up": round(t(76),2), "cards": [round(t(20+i),2) for i in range(3)]}}))
