// Review renders: node tests/shots.mjs <assembly-id> [site]
// Opens the assembly and saves stills at set explode amounts and camera angles,
// for side-by-side comparison with its Haynes figure.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const asm = process.argv[2] || 'engine.head';
const root = path.resolve(process.argv[3] || 'build/viewer');
const out = path.resolve('build/review'); fs.mkdirSync(out, { recursive: true });
const types = { '.html': 'text/html', '.json': 'application/json', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split(/[?#]/)[0]); if (p === '/') p = '/index.html';
  const f = path.join(root, p); if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  let body = fs.readFileSync(f);
  if (p === '/index.html' && !body.toString().trimStart().toLowerCase().startsWith('<!doctype'))
    body = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>' + body + '</body></html>';
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); res.end(body);
}).listen(0);
const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
const errors = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
await page.route('https://cdn.jsdelivr.net/npm/**', route => {
  const m = route.request().url().match(/npm\/(@?[^@]+)@([\d.]+)\/(.+)$/);
  const f = path.resolve('node_modules', m[1], m[3]);
  route.fulfill(fs.existsSync(f) ? { status: 200, contentType: 'text/javascript', body: fs.readFileSync(f) } : { status: 404 });
});
await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: '' }));
await page.goto(`http://127.0.0.1:${server.address().port}/#${(process.env.SELECT || asm).replaceAll('.', '--')}`);
await page.waitForFunction(() => document.getElementById('toast').hidden, null, { timeout: 120000 });
await page.waitForTimeout(Number(process.env.SETTLE || 1500));   // SETTLE=ms: the car view keeps loading after the toast hides
const views = process.env.VIEWS ? JSON.parse(process.env.VIEWS) : [
  { name: 'assembled', explode: 0 },
  { name: 'explode-35', explode: 35 },
  { name: 'explode-100', explode: 100 },
];
for (const v of views) {
  await page.fill('#explode', String(v.explode), { timeout: 600000 }); await page.dispatchEvent('#explode', 'input');
  if (v.camera) await page.evaluate(c => window.mgbCamera && window.mgbCamera(c), v.camera);
  await page.waitForTimeout(1200);
  const box = await page.locator('#stage').boundingBox();
  await page.screenshot({ path: `${out}/${asm}-${v.name}.png`, clip: box, timeout: 120000 });
}
await browser.close(); server.close();
console.log(errors.length ? 'ERRORS\n' + errors.join('\n') : 'ok', '->', out);
