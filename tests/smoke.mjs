// Viewer smoke test: node tests/smoke.mjs [build/viewer]
// Serves the bundle, maps jsDelivr npm URLs to the same files in node_modules,
// opens the page at laptop and phone sizes, opens every assembly, explodes it,
// selects every part, and fails on any console error.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const root = path.resolve(process.argv[2] || 'build/viewer');
const shots = path.resolve('build/shots'); fs.mkdirSync(shots, { recursive: true });
const types = { '.html': 'text/html', '.json': 'application/json', '.glb': 'model/gltf-binary', '.js': 'text/javascript' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split(/[?#]/)[0]);
  if (p === '/') p = '/index.html';
  const f = path.join(root, p);
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  let body = fs.readFileSync(f);
  // the artifact host wraps the page in a doctype skeleton; mimic it
  if (p === '/index.html' && !body.toString().trimStart().toLowerCase().startsWith('<!doctype')) body = '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>' + body + '</body></html>';
  res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); res.end(body);
}).listen(0);
const base = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
const errors = [];
const reg = JSON.parse(fs.readFileSync(path.join(root, 'registry.json')));
const assemblies = Object.values(reg.nodes).filter(n => n.kind === 'assembly');
const parts = Object.values(reg.nodes).filter(n => n.kind === 'part');

for (const [name, vp] of [['laptop', { width: 1366, height: 820 }], ['phone', { width: 390, height: 844 }]]) {
  const page = await browser.newPage({ viewport: vp, reducedMotion: 'reduce' });   // camera snaps instead of flying
  page.on('console', m => { if (m.type() === 'error') errors.push(`${name}: ${m.text()}`); });
  page.on('pageerror', e => errors.push(`${name}: ${e.message}`));
  await page.route('https://cdn.jsdelivr.net/npm/**', route => {
    const m = route.request().url().match(/npm\/(@?[^@]+)@([\d.]+)\/(.+)$/);
    const f = path.resolve('node_modules', m[1], m[3]);
    if (!fs.existsSync(f)) return route.fulfill({ status: 404 });
    route.fulfill({ status: 200, contentType: 'text/javascript', body: fs.readFileSync(f) });
  });
  await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: '' }));
  await page.goto(base);
  await page.waitForFunction(() => document.getElementById('toast').hidden, null, { timeout: 30000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${shots}/${name}-start.png` });
  for (const a of assemblies) {
    await page.evaluate(id => { location.hash = '#' + id.replaceAll('.', '--'); }, a.id);
    await page.waitForTimeout(600);
    await page.fill('#explode', '100'); await page.dispatchEvent('#explode', 'input');
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${shots}/${name}-${a.id}-exploded.png` });
    const st = await page.evaluate(id => window.mgbStatus && [window.mgbStatus.matched[id], window.mgbStatus.expected[id]], a.id);
    if (!st || st[0] !== st[1] || !st[1]) errors.push(`${name}: ${a.id} matched ${st && st[0]} of ${st && st[1]} instances`);
    await page.fill('#explode', '0'); await page.dispatchEvent('#explode', 'input');
  }
  // Software GL renders a laptop-sized canvas slowly, so the laptop pass samples every
  // eighth card and the phone pass (small canvas) checks them all.
  const cards = name === 'laptop' ? parts.filter((_, k) => k % 8 === 0) : parts;
  console.log(`${name}: assemblies ok, checking ${cards.length} part cards`);
  for (const p of cards) {
    await page.evaluate(id => { location.hash = '#' + id.replaceAll('.', '--'); }, p.id);
    await page.waitForTimeout(150);
    const title = await page.textContent('#card h3');
    if (title !== p.name) errors.push(`${name}: card shows "${title}" for ${p.id}`);
  }
  console.log(`${name}: part cards done`);
  await page.screenshot({ path: `${shots}/${name}-card.png` });
  // the view must respond to a drag right after a part has been selected (camera fly-to)
  const box = await page.locator('#stage canvas').boundingBox();
  const before = await page.evaluate(() => window.mgbCameraPos && window.mgbCameraPos());
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down(); await page.mouse.move(box.x + box.width / 2 + 120, box.y + box.height / 2 + 40, { steps: 8 }); await page.mouse.up();
  await page.waitForTimeout(1500);
  const after = await page.evaluate(() => window.mgbCameraPos && window.mgbCameraPos());
  if (!before || !after || Math.hypot(...before.map((v, k) => v - after[k])) < 1e-4) errors.push(`${name}: dragging did not move the view`);
  await page.close();
}
await browser.close(); server.close();
if (errors.length) { console.error('FAIL\n' + errors.join('\n')); process.exit(1); }
console.log(`PASS: ${assemblies.length} assemblies, ${parts.length} parts, laptop and phone, no console errors`);
