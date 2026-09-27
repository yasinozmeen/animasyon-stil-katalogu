// node render.mjs <outDir> [fps=30] [t0=0] [t1=66] [workers=4] [times=comma list]
import { createRequire } from 'module';
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), '@playwright/test'));
const dir = path.dirname(new URL(import.meta.url).pathname);
const [outDir, fpsA = '30', t0A = '0', t1A = '66', wA = '4', timesA] = process.argv.slice(2);
const fps = +fpsA, t0 = +t0A, t1 = +t1A, workers = +wA;
fs.mkdirSync(outDir, { recursive: true });
let jobs;
if (timesA) jobs = timesA.split(',').map(s => ({ t: +s, file: path.join(outDir, `t_${(+s).toFixed(2)}.jpg`) }));
else { jobs = []; const n0 = Math.round(t0 * 30), n1 = Math.round(t1 * 30), stp = Math.round(30 / fps);
  for (let n = n0; n < n1; n += stp) jobs.push({ t: n / 30, file: path.join(outDir, `${String(n).padStart(5, '0')}.jpg`) }); }
const exe = (() => {
  const base = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
  const dirs = fs.readdirSync(base).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse();
  for (const d of dirs) { const p = path.join(base, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell'); if (fs.existsSync(p)) return p; }
})();
const browser = await chromium.launch({ executablePath: exe });
const t = Date.now();
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => console.log('[err]', e.message));
  page.on('console', m => { if (m.type() === 'error') console.log('[console]', m.text()); });
  await page.goto('file://' + path.join(dir, 'anim.html'));
  await page.evaluate(() => window.ready);
  for (let i = w; i < jobs.length; i += workers) {
    const b64 = await page.evaluate(j => window.draw(j), jobs[i]);
    fs.writeFileSync(jobs[i].file, Buffer.from(b64, 'base64'));
  }
}));
await browser.close();
console.log('drew', jobs.length, 'in', ((Date.now() - t) / 1000).toFixed(1), 's');
