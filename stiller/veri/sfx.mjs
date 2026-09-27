// node sfx.mjs → anim.html içindeki window.SFX olaylarını sfx.json'a yazar
import { createRequire } from 'module'; import { execSync } from 'child_process'; import fs from 'fs'; import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), '@playwright/test'));
const dir = path.dirname(new URL(import.meta.url).pathname);
const base = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
const d = fs.readdirSync(base).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse()[0];
const browser = await chromium.launch({ executablePath: path.join(base, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell') });
const page = await browser.newPage(); await page.goto('file://' + path.join(dir, 'anim.html')); await page.evaluate(() => window.ready);
fs.writeFileSync(path.join(dir, 'sfx.json'), JSON.stringify(await page.evaluate(() => window.SFX)));
await browser.close(); console.log('sfx.json yazıldı');
