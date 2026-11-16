// node capture.mjs <outdir> <group>=<a.html,b.html,...> ...
// shoot.mjs of the mockups-before-code skill, for a WebGL page: waits for the state script and a
// few frames before each shot, adds the wide screen (1280 × 800), and reports page errors.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/trans/.claude/skills/mockups-before-code/tools/package.json');
const { chromium } = require('playwright');
const AxeBuilder = require('@axe-core/playwright').default;

const [out, ...groups] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const CELLS = [{ w: 390, h: 844, s: 'light' }, { w: 390, h: 844, s: 'dark' }, { w: 320, h: 640, s: 'light' },
  { w: 320, h: 640, s: 'dark' }, { w: 1280, h: 800, s: 'light' }, { w: 1280, h: 800, s: 'dark' }];
const only = process.env.CELLS ? process.env.CELLS.split(',').map(Number) : null;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const report = [];
for (const g of groups) {
  const [name, list] = g.split('=');
  const files = list.split(',');
  for (const c of CELLS.filter((_, i) => !only || only.includes(i))) {
    const shots = [];
    for (const f of files) {
      const ctx = await browser.newContext({ viewport: { width: c.w, height: c.h }, colorScheme: c.s, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      page.on('pageerror', (e) => report.push(`${path.basename(f)} ${c.w} ${c.s}: page error ${e.message}`));
      await page.goto(pathToFileURL(path.resolve(f)).href);
      await page.waitForSelector('html[data-ready="1"]', { timeout: 20000 });
      await page.waitForTimeout(900);
      const png = path.join(out, `_${name}-${path.basename(f, '.html')}-${c.w}-${c.s}.png`);
      await page.screenshot({ path: png });
      shots.push(png);
      const r = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice']).analyze();
      for (const v of r.violations) report.push(`${name} ${path.basename(f)} ${c.w} ${c.s}: ${v.id} — ${v.nodes.map(n => n.target.join(' ')).join(' | ')}`);
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)) report.push(`${path.basename(f)} ${c.w} ${c.s}: horizontal scroll`);
      const inner = await page.evaluate(() => [...document.querySelectorAll('body *')]
        .filter((e) => /auto|scroll/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 1)
        .map((e) => e.tagName.toLowerCase() + (e.id ? '#' + e.id : '')));
      if (inner.length) report.push(`${path.basename(f)} ${c.w} ${c.s}: content scrolls inside ${inner.join(', ')}`);
      await ctx.close();
    }
    const ctx = await browser.newContext({ viewport: { width: 400, height: 400 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    const imgs = shots.map(p => `<img src="data:image/png;base64,${fs.readFileSync(p).toString('base64')}">`).join('');
    await page.setContent(`<body style="margin:0;background:#888;display:flex;flex-wrap:wrap;gap:24px;padding:24px;align-items:flex-start;width:${c.w > 800 ? 2*c.w + 72 : 4*c.w + 120}px">${imgs}</body>`);
    await page.waitForLoadState('load');
    const H = await page.evaluate(() => document.body.scrollHeight);
    const W = await page.evaluate(() => document.body.scrollWidth);
    const parts = Math.ceil(H / 1800);
    for (let i = 0; i < parts; i++) {
      await page.screenshot({ path: path.join(out, `${name}-${c.w}-${c.s}${parts > 1 ? `-part${i + 1}` : ''}.png`), fullPage: true,
        clip: { x: 0, y: i * 1800, width: W, height: Math.min(1800, H - i * 1800) } });
    }
    await ctx.close();
  }
}
await browser.close();
fs.writeFileSync(path.join(out, 'report.txt'), report.join('\n') || 'no violations');
console.log(report.join('\n') || 'no violations');
