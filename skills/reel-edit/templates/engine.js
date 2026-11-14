/* Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE) */
/* reel-edit motion engine v2 (2026-11-14). Shared by split.html (and any page that links it).
   ALL TIMES ARE TIMELINE SECONDS of the finished Edits timeline (after cuts + speed).
   The page must contain .scene elements; the renderer calls window.__seek(t) and reads window.__duration / __hole(s).

   What it animates:
     .scene[data-in][data-out] ......... a page (hard cut in, hard cut out). Modes: .split (panel + creator card),
                                         .face (creator full screen), .full (panel only, voiceover reels)
       [data-zoom="t1,t2"] [data-zoom-amt=".07"]  punch-in on the panel (+7% per beat, 0.3 s ease, holds to the cut)
     .title[data-in][data-out] ......... top headline, lives OUTSIDE scenes so it can persist across pages
       .acc ............................ accent word (serif italic, underline draws on)
     [data-in] [data-anim=pop|rise|fade|slide|drop|none] [data-dur] [data-out] ... element entry
     .seam[data-words="t word|t word*"] . short captions (1-2 words at a time); word* = keyword (accent colour)
                                         [data-max=2] words per chunk, [data-end] when the last chunk leaves
     .cap[data-cin][data-cout] > .ln > .w[data-t] ... big caption stack (keyword lines .ln.kw ghost in, then pop)
     .l1/.l2[data-words] ............... paper-style two-line headline (legacy, still supported)
     mark[data-t] ...................... highlighter sweep
     .count[data-t data-dur data-from data-to data-dec data-pre data-suf] ... count-up
     .bar[data-t data-pct] > .track > .fill ... growing bar
     .dots[data-t data-dur data-n data-cols] ... grid that fills
     .note[data-in] > svg path ......... hand-drawn arrow/underline draws on (path needs pathLength="1")
     video[data-src][data-in][data-from] B-roll inside a card, seeked frame-exact
     .hole ............................. where the creator shows through (transparent with ?alpha=1)
   SMOOTH MOTION (v3, 2026-11-15, from @motionthekx DctTp5ay2Pa): every entry eases (expo out) with a motion blur that
   clears as it lands; headline words rise out of a blur; scenes WITHOUT a creator window hand over with a 0.3 s blur
   dissolve (data-exit="cut" to opt out) and drift in slowly (data-drift=".02", 0 = off); camera moves:
     .scene[data-cam="t scale x% y% [dur]|…"] ... eased push-in to a point (e.g. the highlighted line of a screenshot)
     .roll[data-in][data-ts="t1,t2"] > span ..... word roller: the active word sharp, neighbours blurred (Motion/Design/Ideas)
     .hlbox[data-t] ............................. highlighter sweep over an IMAGE (real screenshot), placed in % of the card
     data-anim = pop · rise · slide · drop · fade · blur (scale + defocus in) · zoom · none
   FACE CARD (paper v3.1, striver DFr8xtCTCap): ONE persistent polaroid at the bottom, outside the scenes:
     <div class="facecard" data-show="0-7.4,12.7-14.6"><div class="hole"></div></div>   (fades 0.3 s in/out)
     The paper above dissolves page to page while the face window stays still (one Edits transform per segment).
     .scene.face = creator full screen (hole inset 0, hard cut); scenes with .wf keep their content above the card.
   Extra components:
     .meter[data-t data-from data-to data-dur] > .bat + .pct ... battery score that fills and counts
     .strike[data-t] ................... line draws through the word
     .type[data-t data-dur] ............ typewriter reveal (handwritten checklists, search bars)
     .count[data-fmt=mmss] ............. timer count-up (18:36 -> 20:00)
     .prog[data-n data-on] ............. step progress dots
     .fillicon[data-t] ................. icon fills (bookmark on "save")
     .press[data-t] .................... quick press (cursor click)   [data-on-t data-on-text] class "done" from t
     .draw[data-in] > svg path ......... any line/graph that draws on (pathLength="1")
*/
(() => {
const q = new URLSearchParams(location.search); if (q.get('alpha')) document.documentElement.classList.add('alpha');
const clamp = p => Math.max(0, Math.min(1, p)), out3 = p => 1 - Math.pow(1 - p, 3);
const oexp = p => p >= 1 ? 1 : 1 - Math.pow(2, -10 * p), io3 = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const backK = c => p => 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2), back = backK(1.70158), back2 = backK(2.2);
const parse = s => (s || '').split('|').map(x => { const m = x.trim().match(/^(-?[\d.]+)\s+(.*)$/); if (!m) return null;
  let w = m[2], k = false; if (w.endsWith('*')) { k = true; w = w.slice(0, -1); } return { t: +m[1], w, k }; }).filter(Boolean);

// paper headline words (.l1 small line, .l2 big italic line); word* = keyword (class k: accent colour)
document.querySelectorAll('.l1[data-words],.l2[data-words]').forEach(el => { el.innerHTML = '';
  parse(el.dataset.words).forEach((x, i) => { const s = document.createElement('span'); s.dataset.t = x.t; s.textContent = (i ? ' ' : '') + x.w; if (x.k) s.className = 'k'; el.appendChild(s); }); });

// seam captions -> chunks of 1-2 words. Keywords always get their own chunk.
document.querySelectorAll('.seam[data-words]').forEach(el => {
  const W = parse(el.dataset.words), max = +(el.dataset.max || 2), chunks = []; let cur = [];
  const flush = () => { if (cur.length) chunks.push(cur); cur = []; };
  W.forEach(x => { if (x.k) { flush(); cur.push(x); flush(); return; }
    cur.push(x); const len = cur.reduce((a, b) => a + b.w.length + 1, 0);
    if (/[.,!?:;]$/.test(x.w) || cur.length >= max || len >= 13) flush(); });
  flush(); el.innerHTML = '';
  chunks.forEach((c, i) => { const d = document.createElement('div'); d.className = 'chunk'; d.dataset.t = c[0].t;
    const last = c[c.length - 1].t, nxt = i + 1 < chunks.length ? chunks[i + 1][0].t : (+el.dataset.end || last + 0.9);
    d.dataset.e = Math.min(nxt - .02, last + 1.1);
    c.forEach((x, j) => { const s = document.createElement('span'); s.textContent = (j ? ' ' : '') + x.w; if (x.k) s.className = 'k'; d.appendChild(s); });
    el.appendChild(d); });
});
document.querySelectorAll('.dots').forEach(d => { d.style.gridTemplateColumns = `repeat(${d.dataset.cols || 25},1fr)`; d.innerHTML = '<i></i>'.repeat(+d.dataset.n || 400); });
// progress dots, typewriter text
document.querySelectorAll('.prog').forEach(p => { const n = +(p.dataset.n || 4), on = +(p.dataset.on || 1); p.innerHTML = Array.from({ length: n }, (_, i) => `<i${i < on ? ' class="on"' : ''}></i>`).join(''); });
document.querySelectorAll('.type').forEach(el => { el.dataset.full = el.textContent; });
const mmss = v => { v = Math.round(v); return Math.floor(v / 60) + ':' + String(v % 60).padStart(2, '0'); };

if (q.get('under') && !q.get('alpha')) { const u = document.createElement('video'); u.className = 'under'; u.muted = true; u.src = q.get('under'); document.body.prepend(u); }
const under = document.querySelector('video.under');
// LOCAL RENDER (no Edits): <div class="facecard" data-src="face-cut.mp4" data-focus="52% 30%" …> draws the timeline-aligned
// face video inside the card (object-fit cover, data-focus = where the face is), so an opaque render is the finished video.
const faceSrc = q.get('face') || null;
document.querySelectorAll('.facecard').forEach(f => { const src = f.dataset.src || faceSrc; if (!src) return; const h = f.querySelector('.hole'); if (!h) return;
  const v = document.createElement('video'); v.className = 'facevid'; v.muted = true; v.playsInline = true; v.src = src;
  v.style.cssText = `width:100%;height:100%;object-fit:cover;object-position:${f.dataset.focus || '50% 30%'};display:block;border-radius:inherit`; h.appendChild(v); });
const faceVids = [...document.querySelectorAll('video.facevid')];
const facecards = [...document.querySelectorAll('.facecard[data-show]')].map(f => ({ el: f, base: f.className,
  seg: f.dataset.show.split('|').map(x => { const [r, pos = 'bottom', shape = 'polaroid'] = x.trim().split(/\s+/); const [a, b] = r.split('-').map(Number); return { a, b, pos, shape }; }) }));
// each scene learns where the face is when it starts (f-top / f-center / f-bottom / f-full / f-none) to lay out its content
document.querySelectorAll('.scene').forEach(sc => { const t = +sc.dataset.in + .05; let pos = 'none';
  facecards.forEach(({ seg }) => seg.forEach(g => { if (t >= g.a && t < g.b) pos = g.pos; })); sc.classList.add('f-' + pos); if (pos !== 'none') sc.classList.add('f-' + (facecards[0].seg.find(g => t >= g.a && t < g.b) || {}).shape); });
// subtitle captions (striver DfCwrlZz5jz): a line under the media, words appear as spoken, keyword* in a yellow box
document.querySelectorAll('.sub[data-words]').forEach(el => { const W = parse(el.dataset.words), max = +(el.dataset.max || 5), ch = []; let cur = [];
  W.forEach(x => { cur.push(x); if (/[.,!?:;]$/.test(x.w) || cur.length >= max) { ch.push(cur); cur = []; } }); if (cur.length) ch.push(cur); el.innerHTML = '';
  ch.forEach((c, i) => { const d = document.createElement('div'); d.className = 'line'; d.dataset.t = c[0].t; d.dataset.e = i + 1 < ch.length ? ch[i + 1][0].t - .02 : (+el.dataset.end || 1e9);
    c.forEach((x, j) => { const sp = document.createElement('span'); sp.dataset.t = x.t; sp.textContent = x.w; if (x.k) sp.className = 'k'; d.appendChild(sp); if (j < c.length - 1) d.appendChild(document.createTextNode(' ')); });
    el.appendChild(d); }); });
const scenes = [...document.querySelectorAll('.scene')], titles = [...document.querySelectorAll('.title')], paper = document.querySelector('.paper');
window.__duration = Math.max(...scenes.map(s => +s.dataset.out));

function anim(el, T) { const tin = +el.dataset.in, d = +(el.dataset.dur || .55), p = clamp((T - tin) / d), k = el.dataset.anim || 'fade';
  const o = el.dataset.out ? clamp((+el.dataset.out - T) / .3) : 1, vis = T >= tin, e = oexp(p); let tf = '', bl = (1 - e) * .9;
  if (k === 'pop') { tf = `scale(${(.72 + .28 * back(p)).toFixed(4)})`; bl = (1 - e) * .7; }
  else if (k === 'rise') tf = `translateY(${((1 - e) * 6).toFixed(3)}rem)`;
  else if (k === 'slide') tf = `translateX(${((1 - e) * -10).toFixed(3)}rem)`;
  else if (k === 'drop') tf = `translateY(${((1 - back(p)) * -8).toFixed(3)}rem)`;
  else if (k === 'blur') { tf = `scale(${(1.08 - .08 * e).toFixed(4)})`; bl = (1 - e) * 2.2; }
  else if (k === 'zoom') tf = `scale(${(.84 + .16 * e).toFixed(4)})`;
  if (k === 'none') bl = 0; bl += (1 - o) * 1.2;   // exits (data-out) defocus too
  el.style.opacity = vis ? Math.min(k === 'none' ? 1 : clamp(p * 1.8), o) : 0; el.style.transform = tf;
  el.style.filter = vis && bl > .01 ? `blur(${bl.toFixed(3)}rem)` : ''; }
const EXIT = .3;

window.__seek = async T => { const waits = []; let holes = [], fades = [];
  facecards.forEach(({ el, base, seg }) => { let a = 0, cur = null;
    seg.forEach(g => { if (T < g.a || T >= g.b) return; cur = g;   // fade only where the face appears/leaves, not between touching segments
      const fin = g.a <= 0 || seg.some(h => Math.abs(h.b - g.a) < .02) ? 1 : clamp((T - g.a) / .3), fout = seg.some(h => Math.abs(h.a - g.b) < .02) ? 1 : clamp((g.b - T) / .3);
      a = Math.min(fin, fout); });
    if (cur) el.className = `${base} pos-${cur.pos} ${cur.shape}`;
    const e = cur && cur.pos === 'full' ? 1 : io3(a); el.style.visibility = a > 0 ? 'visible' : 'hidden'; el.style.opacity = e.toFixed(3);
    if (a > 0) el.querySelectorAll('.hole').forEach(h => { holes.push(h); fades.push(e); }); });
  faceVids.forEach(v => { if (Math.abs(v.currentTime - T) > .001) { waits.push(new Promise(r => { v.addEventListener('seeked', r, { once: true }); setTimeout(r, 3000); })); v.currentTime = T; } });
  if (under && Math.abs(under.currentTime - T) > .001) { waits.push(new Promise(r => { under.addEventListener('seeked', r, { once: true }); setTimeout(r, 3000); })); under.currentTime = T; }
  titles.forEach(ti => { const on = T >= +ti.dataset.in && T < +ti.dataset.out; ti.style.visibility = on ? 'visible' : 'hidden'; if (!on) return;
    const p = +ti.dataset.in <= 0 ? 1 : clamp((T - +ti.dataset.in) / .35); ti.style.opacity = clamp(p * 1.8); ti.style.transform = `translateY(${(1 - out3(p)) * -2}rem)`;
    ti.querySelectorAll('.acc').forEach(a => a.style.setProperty('--u', +ti.dataset.in <= 0 ? 1 : out3(clamp((T - +ti.dataset.in - .25) / .45)).toFixed(3))); });
  for (const s of scenes) { const tin = +s.dataset.in, tout = +s.dataset.out, creator = !!s.querySelector('.hole'),
      soft = !creator && s.dataset.exit !== 'cut' && tout < window.__duration, on = T >= tin && T < tout + (soft ? EXIT : 0);
    s.style.visibility = on ? 'visible' : 'hidden';
    if (!on) { s.querySelectorAll('.cap,.seam .chunk,.sub .line').forEach(c => c.style.visibility = 'hidden'); continue; }
    s.querySelectorAll('[data-in]').forEach(el => anim(el, Math.min(T, tout - .001)));
    const z = (s.dataset.zoom || '').split(',').filter(Boolean).map(Number), amt = +(s.dataset.zoomAmt || .07);
    let sc = 1; z.forEach(b => { sc += amt * oexp(clamp((T - (b - .12)) / .35)); });
    if (creator) { // punch-in on the panel only: the creator window must stay fixed for the Edits transforms
      const zt = s.querySelector('.panel') || s; zt.style.transform = sc === 1 ? '' : `scale(${sc.toFixed(4)})`; }
    else { // smooth camera: slow drift + punch-ins + eased push to a point, then the blur dissolve out
      const dr = s.dataset.drift !== undefined ? +s.dataset.drift : .02; sc *= 1 + dr * io3(clamp((T - tin) / Math.max(.5, tout - tin)));
      let cs = 1, px = 50, py = 45;
      (s.dataset.cam || '').split('|').map(x => x.trim().split(/\s+/).map(parseFloat)).filter(k => k.length >= 2 && !isNaN(k[0])).forEach(([t, k, x = 50, y = 45, d = .8]) => {
        const p = io3(clamp((T - t) / d)); if (p > 0) { cs += (k - cs) * p; px += (x - px) * p; py += (y - py) * p; } });
      const S = sc * cs, xp = innerWidth * px / 100, yp = innerHeight * py / 100, x = clamp((T - tout) / EXIT);
      // the camera moves the CONTENT; the headline (.l1/.l2) stays put so it never enters the top UI zone
      [...s.children].filter(c => !c.matches('.l1,.l2,.seam,.sub,.title,script')).forEach(c => {
        const ox = c.offsetLeft + c.offsetWidth / 2, oy = c.offsetTop + c.offsetHeight / 2;
        c.style.translate = S === 1 ? '' : `${((ox - xp) * (S - 1)).toFixed(2)}px ${((oy - yp) * (S - 1)).toFixed(2)}px`; c.style.scale = S === 1 ? '' : S.toFixed(5); });
      s.style.transform = x > 0 ? `translateY(${(-x * innerHeight * .02).toFixed(2)}px)` : '';
      s.style.opacity = soft ? (1 - io3(x)).toFixed(3) : ''; s.style.filter = x > 0 ? `blur(${(x * 1.6).toFixed(3)}rem)` : ''; }
    s.querySelectorAll('.roll[data-ts]').forEach(r => { const ts = r.dataset.ts.split(',').map(Number), kids = [...r.children];
      let pos = 0; ts.forEach(t => { pos += io3(clamp((T - t) / .45)); });
      kids.forEach((c, j) => { const d = Math.abs(j - pos); c.style.transform = `translateY(calc(${((j - pos) * 1.12).toFixed(4)}em - 50%)) scale(${(1 - .14 * Math.min(d, 1.5)).toFixed(4)})`;
        c.style.opacity = clamp(1 - .62 * d).toFixed(3); c.style.filter = d > .02 ? `blur(${(d * .06).toFixed(3)}em)` : ''; }); });
    s.querySelectorAll('.sub .line').forEach(l => { const on2 = T >= +l.dataset.t - .02 && T < +l.dataset.e; l.style.visibility = on2 ? 'visible' : 'hidden'; if (!on2) return;
      l.querySelectorAll('span[data-t]').forEach(w => { const f = oexp(clamp((T - +w.dataset.t) / .22)); w.style.opacity = clamp(.15 + f).toFixed(3);
        w.style.filter = f < .99 ? `blur(${((1 - f) * .4).toFixed(3)}rem)` : ''; if (w.classList.contains('k')) w.style.setProperty('--s', oexp(clamp((T - +w.dataset.t) / .3)).toFixed(3)); }); });
    s.querySelectorAll('.hlbox[data-t]').forEach(h => h.style.setProperty('--s', oexp(clamp((T - +h.dataset.t) / .45)).toFixed(3)));
    s.querySelectorAll('.seam .chunk').forEach(c => { const t = +c.dataset.t, on2 = T >= t - .02 && T < +c.dataset.e; c.style.visibility = on2 ? 'visible' : 'hidden';
      if (on2) { const p = clamp((T - t) / .12); c.style.transform = `scale(${(.86 + .14 * back(p)).toFixed(4)})`; } });
    s.querySelectorAll('.cap').forEach(c => { const on2 = T >= +c.dataset.cin && T < +c.dataset.cout; c.style.visibility = on2 ? 'visible' : 'hidden'; if (!on2) return;
      c.querySelectorAll('.w').forEach(w => { const t = +w.dataset.t, kw = w.parentElement.classList.contains('kw');
        if (kw) { const gs = w.dataset.g !== undefined ? +w.dataset.g : t - .3, g = clamp((T - gs) / .1), f = clamp((T - t) / .22);
          w.style.opacity = g ? (.18 + .82 * f) : 0; w.style.filter = `blur(${((1 - f) * .3).toFixed(3)}rem)`;
          w.style.transform = `scale(${(f > 0 ? (.82 + .18 * back2(f)) : .82).toFixed(4)})`; }
        else { const f = clamp((T - t) / .14); w.style.opacity = f; w.style.transform = `translateY(${((1 - out3(f)) * 1.4).toFixed(3)}rem)`; } }); });
    s.querySelectorAll('.l1 span,.l2 span').forEach(sp => { const t = +sp.dataset.t, l2 = sp.parentElement.classList.contains('l2');
      if (t <= 0) { sp.style.opacity = 1; sp.style.filter = ''; sp.style.transform = ''; return; }   // hook words: readable on frame 1
      if (l2) { const g = clamp((T - (t - .35)) / .12), f = oexp(clamp((T - t) / .3)); sp.style.opacity = g ? (.2 + .8 * f).toFixed(3) : 0;
        sp.style.filter = f < .99 ? `blur(${((1 - f) * .5).toFixed(3)}rem)` : ''; sp.style.transform = `translateY(${((1 - f) * .8).toFixed(3)}rem)`; }
      else { const f = oexp(clamp((T - t) / .26)); sp.style.opacity = clamp(f * 1.4).toFixed(3); sp.style.transform = `translateY(${((1 - f) * 1.6).toFixed(3)}rem)`;
        sp.style.filter = f < .99 ? `blur(${((1 - f) * .6).toFixed(3)}rem)` : ''; } });
    s.querySelectorAll('mark[data-t]').forEach(m => { m.style.backgroundSize = `${out3(clamp((T - +m.dataset.t) / .4)) * 100}% 82%`; });
    s.querySelectorAll('.count').forEach(c => { const p = out3(clamp((T - +c.dataset.t) / +(c.dataset.dur || 1.5))), v = +c.dataset.from + (+c.dataset.to - +c.dataset.from) * p;
      c.textContent = (c.dataset.pre || '') + (c.dataset.fmt === 'mmss' ? mmss(v) : v.toFixed(+(c.dataset.dec || 0)).replace(/\B(?=(\d{3})+(?!\d))/g, ',')) + (c.dataset.suf || ''); });
    // ---- extra components ----
    if (s.classList.contains('blur')) s.style.setProperty('--b', out3(clamp((T - +s.dataset.in) / .3)).toFixed(3));   // style-03 blur pages
    s.querySelectorAll('.strike[data-t]').forEach(e => e.style.setProperty('--s', out3(clamp((T - +e.dataset.t) / .3)).toFixed(3)));
    s.querySelectorAll('.meter[data-t]').forEach(m => { const v = +m.dataset.from + (+m.dataset.to - +m.dataset.from) * out3(clamp((T - +m.dataset.t) / +(m.dataset.dur || .8)));
      m.querySelector('.bat').style.setProperty('--p', v.toFixed(1) + '%'); const pc = m.querySelector('.pct'); if (pc) pc.textContent = Math.round(v) + '%'; });
    s.querySelectorAll('.type[data-t]').forEach(e => { const f = e.dataset.full, d = +(e.dataset.dur || f.length * .035);
      e.textContent = f.slice(0, Math.round(f.length * clamp((T - +e.dataset.t) / d))); });
    s.querySelectorAll('.fillicon[data-t]').forEach(e => e.style.setProperty('--f', out3(clamp((T - +e.dataset.t) / .3)).toFixed(3)));
    s.querySelectorAll('.press[data-t]').forEach(e => { const d = T - +e.dataset.t; e.style.transform = d >= 0 && d < .24 ? `scale(${(1 - .16 * Math.sin(Math.PI * d / .24)).toFixed(3)})` : ''; });
    s.querySelectorAll('[data-on-t]').forEach(e => { const on = T >= +e.dataset.onT; e.classList.toggle('done', on); if (e.dataset.onText) { e.dataset.offText ??= e.textContent; e.textContent = on ? e.dataset.onText : e.dataset.offText; } });
    s.querySelectorAll('.bar').forEach(b => { b.querySelector('.fill').style.width = out3(clamp((T - +b.dataset.t) / .9)) * +b.dataset.pct + '%'; });
    s.querySelectorAll('.dots').forEach(d => { const n = Math.round(out3(clamp((T - +d.dataset.t) / +(d.dataset.dur || 1.5))) * d.children.length); [...d.children].forEach((i, j) => i.classList.toggle('on', j < n)); });
    s.querySelectorAll('.note,.draw').forEach(n => { const p = out3(clamp((T - +n.dataset.in - .1) / .45)); n.querySelectorAll('path').forEach(pa => { pa.style.strokeDasharray = 1; pa.style.strokeDashoffset = (1 - p).toFixed(3); }); });
    s.querySelectorAll('video[data-src]').forEach(v => { if (!v.src) v.src = v.dataset.src; v.muted = true; const tt = Math.max(0, T - +(v.dataset.in || s.dataset.in)) + +(v.dataset.from || 0);
      if (Math.abs(v.currentTime - tt) > .001) waits.push(new Promise(r => { v.addEventListener('seeked', r, { once: true }); setTimeout(r, 3000); })); v.currentTime = tt; });
    s.querySelectorAll('.hole').forEach(h => { holes.push(h); fades.push(1); }); }
  // cut every creator window out of the paper so the creator clip (main track in Edits) shows through
  if (paper) { if (holes.length && q.get('alpha')) { const rs = holes.map(h => h.getBoundingClientRect());
      const imgs = ['linear-gradient(#000,#000)', ...rs.map((_, i) => `linear-gradient(rgba(0,0,0,${fades[i].toFixed(3)}),rgba(0,0,0,${fades[i].toFixed(3)}))`)].join(',');
      paper.style.webkitMaskImage = paper.style.maskImage = imgs; paper.style.maskSize = ['100% 100%', ...rs.map(r => `${r.width}px ${r.height}px`)].join(',');
      paper.style.maskPosition = ['0 0', ...rs.map(r => `${r.left}px ${r.top}px`)].join(','); paper.style.maskRepeat = 'no-repeat'; paper.style.maskComposite = 'exclude'; }
    else paper.style.maskImage = paper.style.webkitMaskImage = 'none'; }
  await Promise.all(waits);
  const norm = h => { const r = h.getBoundingClientRect(); return { x: +((r.left + r.width / 2) / innerWidth).toFixed(4), y: +((r.top + r.height / 2) / innerHeight).toFixed(4), w: +(r.width / innerWidth).toFixed(4), h: +(r.height / innerHeight).toFixed(4) }; };
  window.__hole = holes.length ? norm(holes[0]) : null; };
if (!q.has('render')) { const t0 = performance.now(); const loop = async () => { await window.__seek(((performance.now() - t0) / 1000) % window.__duration); requestAnimationFrame(loop); }; loop(); }
})();
