// node events.mjs → anim.html içindeki window.events() çıktısını events.json'a yazar (ses için)
import { createRequire } from 'module'; import { execSync } from 'child_process'; import path from 'path'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), '@playwright/test'));
const dir = path.dirname(new URL(import.meta.url).pathname);
const base = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
const d = fs.readdirSync(base).filter(d => d.startsWith('chromium_headless_shell-')).sort().reverse()[0];
const b = await chromium.launch({ executablePath: path.join(base, d, 'chrome-headless-shell-mac-arm64/chrome-headless-shell') });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto('file://' + path.join(dir, 'anim.html')); await p.evaluate(() => window.ready);
fs.writeFileSync(path.join(dir, 'events.json'), JSON.stringify(await p.evaluate(() => window.events())));
await b.close();
