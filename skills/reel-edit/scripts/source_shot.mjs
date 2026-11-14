#!/usr/bin/env node
// Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
// Real, crisp screenshots of a SOURCE for the reel: a tweet, an Instagram post, or one paragraph/element of any page.
// No login, no video download: tweets and IG posts are shot from their OFFICIAL EMBED pages (what any site embeds).
//
//   node source_shot.mjs <url> out.png [--text "exact phrase"] [--sel "css"] [--scale 3] [--width 1100] [--pad 24]
//                                     [--wait 3500] [--dark] [--full]
//   x.com/…/status/ID  or twitter.com/…  -> platform.twitter.com/embed/Tweet.html?id=ID   (crops to the tweet card)
//   instagram.com/p|reel/CODE           -> instagram.com/p/CODE/embed/captioned/          (crops to the post card)
//   anything else                       -> the page; --text crops to the smallest block (p, li, blockquote, h1-h4,
//                                          figure, td) that contains the phrase; --sel crops to a CSS selector;
//                                          --full = whole viewport. It also prints the phrase's box inside the
//                                          crop (x,y,w,h in %) so the reel can sweep a highlighter over it (.hlbox).
// Default scale 3 (a 1100-px-wide crop becomes 3300 px): sharp at 1440x2560 even when the camera pushes in.
// Log every shot in b-rools/<topic>/CREDITS.md (url + date). Screenshots only: never download Instagram/X video.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
if (args.length < 2) { console.error('usage: node source_shot.mjs URL out.png [--text phrase] [--sel css] [--scale 3] [--width 1100] [--pad 24] [--wait 3500] [--dark] [--full]'); process.exit(1); }
const [src, out] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i > -1 ? args[i + 1] : d; };
const flag = k => args.includes('--' + k);
const SCALE = +opt('scale', 3), PAD = +opt('pad', 24), WAIT = +opt('wait', 3500);
let url = src, sel = opt('sel', ''), width = +opt('width', 1100), kind = 'web';
const tw = src.match(/(?:x|twitter)\.com\/[^/]+\/status(?:es)?\/(\d+)/);
const ig = src.match(/instagram\.com\/(?:[^/]+\/)?(?:p|reel|tv)\/([\w-]+)/);
if (tw) { kind = 'tweet'; width = +opt('width', 560); url = `https://platform.twitter.com/embed/Tweet.html?id=${tw[1]}&theme=${flag('dark') ? 'dark' : 'light'}&dnt=true&hideThread=true&lang=en`; sel ||= 'article'; }
else if (ig) { kind = 'instagram'; width = +opt('width', 560); url = `https://www.instagram.com/p/${ig[1]}/embed/captioned/`; sel ||= '.Embed, .EmbedFrame, body > div'; }

const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!existsSync(CHROME)) { console.error('Chrome not found; set CHROME=/path/to/chrome'); process.exit(1); }
const prof = mkdtempSync(join(tmpdir(), 'srcshot-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${prof}`, '--hide-scrollbars',
  '--mute-audio', '--no-first-run', '--no-default-browser-check', '--force-color-profile=srgb', `--window-size=${width},2400`, 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });
const cleanup = () => { try { chrome.kill('SIGKILL'); } catch {} try { rmSync(prof, { recursive: true, force: true }); } catch {} };
process.on('exit', cleanup);
const wsUrl = await new Promise((ok, bad) => { let b = ''; const t = setTimeout(() => bad(new Error('Chrome did not start')), 20000);
  chrome.stderr.on('data', d => { b += d; const m = b.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(t); ok(m[1]); } }); });
const ws = new WebSocket(wsUrl); await new Promise((ok, bad) => { ws.onopen = ok; ws.onerror = bad; });
let id = 0; const pend = new Map(), waiters = [];
ws.onmessage = e => { const m = JSON.parse(e.data);
  if (m.id && pend.has(m.id)) { const p = pend.get(m.id); pend.delete(m.id); m.error ? p.bad(new Error(JSON.stringify(m.error))) : p.ok(m.result); }
  else if (m.method) for (const w of [...waiters]) if (w.method === m.method) { waiters.splice(waiters.indexOf(w), 1); w.ok(m.params); } };
const send = (method, params = {}, sessionId) => new Promise((ok, bad) => { const i = ++id; pend.set(i, { ok, bad }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
const once = m => new Promise(ok => waiters.push({ method: m, ok }));
const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId: S } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, S);
await send('Emulation.setDeviceMetricsOverride', { width, height: 2400, deviceScaleFactor: SCALE, mobile: false }, S);
await send('Network.enable', {}, S);
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: flag('dark') ? 'dark' : 'light' }] }, S);
await send('Network.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36' }, S);
const loaded = once('Page.loadEventFired'); await send('Page.navigate', { url }, S);
await Promise.race([loaded, new Promise(r => setTimeout(r, 20000))]);
await new Promise(r => setTimeout(r, WAIT));
const ev = async x => { const r = await send('Runtime.evaluate', { expression: x, awaitPromise: true, returnByValue: true }, S);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error'); return r.result.value; };
// hide cookie banners / login walls that sit on top of article pages
await ev(`(()=>{for(const e of document.querySelectorAll('[id*=cookie i],[class*=cookie i],[id*=consent i],[class*=consent i],[class*=paywall i],[class*=modal i]')){const s=getComputedStyle(e);if(s.position==='fixed'||s.position==='sticky')e.style.display='none'}
 return document.fonts?document.fonts.ready.then(()=>1):1})()`);
const phrase = opt('text', '');
const box = await ev(`(()=>{
  const PH=${JSON.stringify(phrase)}, SEL=${JSON.stringify(sel)}, FULL=${flag('full')};
  const R=e=>{const r=e.getBoundingClientRect();return{x:r.left+scrollX,y:r.top+scrollY,w:r.width,h:r.height}};
  let el=null, hit=null;
  if(PH){const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;const low=PH.toLowerCase();
    while((n=w.nextNode())){const i=n.data.toLowerCase().indexOf(low);if(i>-1){const rg=document.createRange();rg.setStart(n,i);rg.setEnd(n,Math.min(n.data.length,i+PH.length));hit=rg;
      el=n.parentElement.closest('p,li,blockquote,h1,h2,h3,h4,figure,td,article,[data-testid=tweetText]')||n.parentElement;break;}}
    if(!hit){ // phrase split across nodes: match on element text
      const c=[...document.querySelectorAll('p,li,blockquote,h1,h2,h3,h4,td')].filter(e=>e.innerText.toLowerCase().includes(low));c.sort((a,b)=>a.innerText.length-b.innerText.length);el=c[0]||null;}}
  if(SEL){const s=[...document.querySelectorAll(SEL)].filter(e=>e.getBoundingClientRect().height>40);if(s.length)el=(el&&s.find(x=>x.contains(el)))||s[0];}
  if(FULL||!el) return {crop:{x:0,y:0,w:innerWidth,h:Math.min(document.documentElement.scrollHeight,2400)},found:!!el||FULL,hit:null};
  const c=R(el); let h=null; if(hit){const rs=[...hit.getClientRects()];if(rs.length){const x0=Math.min(...rs.map(r=>r.left))+scrollX,y0=Math.min(...rs.map(r=>r.top))+scrollY,
    x1=Math.max(...rs.map(r=>r.right))+scrollX,y1=Math.max(...rs.map(r=>r.bottom))+scrollY;h={x:x0,y:y0,w:x1-x0,h:y1-y0};}}
  return {crop:c,found:true,hit:h,tag:el.tagName};})()`);
if (!box.found) console.error(`warning: ${phrase ? 'phrase' : 'selector'} not found, shooting the viewport`);
const p = PAD, c = { x: Math.max(0, box.crop.x - p), y: Math.max(0, box.crop.y - p), width: box.crop.w + 2 * p, height: box.crop.h + 2 * p, scale: 1 };
const { data } = await send('Page.captureScreenshot', { format: 'png', clip: c, captureBeyondViewport: true }, S);
writeFileSync(out, Buffer.from(data, 'base64'));
const pct = h => h && `x ${((h.x - c.x) / c.width * 100).toFixed(1)}% y ${((h.y - c.y) / c.height * 100).toFixed(1)}% w ${(h.w / c.width * 100).toFixed(1)}% h ${(h.h / c.height * 100).toFixed(1)}%`;
console.log(`${out}  ${kind}  ${Math.round(c.width * SCALE)}x${Math.round(c.height * SCALE)} px  from ${url}`);
if (box.hit) console.log(`phrase box (for .hlbox style): left:${pct(box.hit).split(' ')[1]};top:${pct(box.hit).split(' ')[3]};width:${pct(box.hit).split(' ')[5]};height:${pct(box.hit).split(' ')[7]}`);
ws.close(); cleanup(); process.exit(0);
