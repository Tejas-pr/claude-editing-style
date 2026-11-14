#!/usr/bin/env node
// Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
// Render an HTML animation (templates/paper.html) to video, frame-exact, with no npm packages.
// It drives headless Chrome over the DevTools protocol (Node 22+ has a built-in WebSocket)
// and pipes the frames into ffmpeg.
//
// Usage:
//   node render.mjs page.html out.mp4 [--w 1440 --h 2560 --fps 30 --from 0 --to <dur> --crf 16]   opaque H.264
//   node render.mjs page.html out.mov --alpha [...]   HEVC with alpha (creator .hole is transparent) for an Edits overlay
//   node render.mjs page.html sheet.png --stills 0.5,3,6,9 [--alpha]   one contact sheet (cheap check; alpha shows as magenta)
//   ... --stills ... --under face-cut.mp4   check sheet with the face under the transparent pages (style-03)
//   node render.mjs page.html out.mp4 --face face-cut.mp4   LOCAL render: the face video drawn inside every .facecard
// It prints every change of creator window (one line per page that moves the .hole), for the Edits transforms.
//
// The page must define window.__duration (seconds) and window.__seek(t). The template does this.
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
if (args.length < 2) { console.error('usage: node render.mjs page.html out.mp4|sheet.png [--w --h --fps --from --to --crf --stills]'); process.exit(1); }
const [page, out] = args;
const opt = (k, d) => { const i = args.indexOf('--' + k); return i > -1 ? args[i + 1] : d; };
const ALPHA = args.includes('--alpha');
const W = +opt('w', 1440), H = +opt('h', 2560), FPS = +opt('fps', 30), CRF = opt('crf', '10');
const stills = opt('stills', '') ? opt('stills').split(',').map(Number) : null;
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!existsSync(CHROME)) { console.error('Chrome not found; set CHROME=/path/to/chrome'); process.exit(1); }

const prof = mkdtempSync(join(tmpdir(), 'render-chrome-'));
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=0', `--user-data-dir=${prof}`,
  '--hide-scrollbars', '--mute-audio', '--no-first-run', '--no-default-browser-check',
  '--force-device-scale-factor=1', '--force-color-profile=srgb', `--window-size=${W},${H}`, 'about:blank'],
  { stdio: ['ignore', 'ignore', 'pipe'] });
const cleanup = () => { try { chrome.kill('SIGKILL'); } catch {} try { rmSync(prof, { recursive: true, force: true }); } catch {} };
process.on('exit', cleanup);

const wsUrl = await new Promise((ok, bad) => {
  let buf = ''; const t = setTimeout(() => bad(new Error('Chrome did not start')), 20000);
  chrome.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) { clearTimeout(t); ok(m[1]); } });
});
const ws = new WebSocket(wsUrl);
await new Promise((ok, bad) => { ws.onopen = ok; ws.onerror = bad; });
let id = 0; const pending = new Map(), waiters = [];
ws.onmessage = e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.bad(new Error(JSON.stringify(m.error))) : p.ok(m.result); }
  else if (m.method) for (const w of [...waiters]) if (w.method === m.method) { waiters.splice(waiters.indexOf(w), 1); w.ok(m.params); }
};
const send = (method, params = {}, sessionId) => new Promise((ok, bad) => { const i = ++id; pending.set(i, { ok, bad }); ws.send(JSON.stringify({ id: i, method, params, sessionId })); });
const once = method => new Promise(ok => waiters.push({ method, ok }));

const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
const { sessionId: S } = await send('Target.attachToTarget', { targetId, flatten: true });
await send('Page.enable', {}, S);
if (ALPHA && !stills) await send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } }, S);
await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false }, S);
const url = pathToFileURL(resolve(page)).href + `?render=1&w=${W}&h=${H}` + (opt('theme', '') ? `&theme=${opt('theme')}` : '') + (ALPHA ? '&alpha=1' : '') + (opt('under', '') ? `&under=${encodeURIComponent(opt('under'))}` : '') + (opt('face', '') ? `&face=${encodeURIComponent(opt('face'))}` : '');
const loaded = once('Page.loadEventFired');
await send('Page.navigate', { url }, S);
await loaded;
const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true }, S); if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || 'page error'); return r.result.value; };
await ev('document.fonts.ready.then(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>0))))');
await ev('(async()=>{await window.__seek(0);await new Promise(r=>setTimeout(r,300));return 1})()'); // warm-up: avoids an empty first frame
const dur = await ev('window.__duration');
if (ALPHA && stills) await ev("document.documentElement.style.background='#ff00ff',1"); // magenta = transparent, for checking
if (!dur) throw new Error('page has no window.__duration / __seek');

const from = +opt('from', 0), to = +opt('to', dur);
const times = stills || Array.from({ length: Math.round((to - from) * FPS) }, (_, i) => from + i / FPS);
const tile = `scale=${Math.round(480 * W / H / 2) * 2}:480,tile=${Math.min(times.length, 6)}x${Math.ceil(times.length / 6)}:padding=6:color=gray`;
const ffArgs = stills
  ? ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '25', '-i', '-',
     '-vf', tile, '-frames:v', '1', out]
  : ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
     ...(ALPHA ? ['-c:v', 'hevc_videotoolbox', '-alpha_quality', '0.9', '-q:v', '70', '-tag:v', 'hvc1', '-pix_fmt', 'bgra']
               : ['-c:v', 'libx264', '-preset', 'slow', '-crf', CRF, '-pix_fmt', 'yuv420p']), '-movflags', '+faststart', out];
const ff = spawn('ffmpeg', ffArgs, { stdio: ['pipe', 'inherit', 'inherit'] });
const ffDone = new Promise(ok => ff.on('close', ok));

const t0 = Date.now(); const holes = []; let lastHole = '';
for (let i = 0; i < times.length; i++) {
  await ev(`(async()=>{await window.__seek(${times[i]});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));return 1})()`);
  const { data } = await send('Page.captureScreenshot', ALPHA && !stills ? { format: 'png', captureBeyondViewport: false } : { format: 'jpeg', quality: 95, captureBeyondViewport: false }, S);
  { const h = await ev('JSON.stringify(window.__hole||null)'); if (h !== lastHole) { holes.push(`${(+times[i]).toFixed(2)}s ${h}`); lastHole = h; } } // every change of creator window
  if (!ff.stdin.write(Buffer.from(data, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  if (!stills && i % (FPS * 5) === 0) process.stderr.write(`  ${times[i].toFixed(1)}s / ${to.toFixed(1)}s\n`);
}
ff.stdin.end();
const code = await ffDone;
ws.close(); cleanup();
if (code !== 0) { console.error('ffmpeg failed'); process.exit(1); }
if (holes.some(h => !h.endsWith('null'))) console.log('creator window changes (time: normalised centre x,y and w,h; null = no creator):\n  ' + holes.join('\n  '));
console.log(`${out}  ${times.length} frame(s), ${W}x${H}${stills ? '' : ` @${FPS}fps, ${(to - from).toFixed(2)}s`}, ${((Date.now() - t0) / 1000).toFixed(1)}s`);
process.exit(0);
