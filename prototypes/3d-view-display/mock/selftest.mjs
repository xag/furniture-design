// Drives the prototype as a person would: opens the display settings, ticks Dimensions, opens a
// branch, picks each look for the rest by tapping its word, and checks the page answered each time.
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/trans/.claude/skills/mockups-before-code/tools/package.json');
const { chromium } = require('playwright');
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await (await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true })).newPage();
const errors = []; page.on('pageerror', e => errors.push(e.message));
await page.goto(pathToFileURL(path.resolve('play-A.html')).href);
await page.waitForSelector('html[data-ready="1"]');
const out = {};
await page.getByRole('button', { name: 'Affichage' }).tap();
out.open = await page.locator('#display').evaluate(e => e.classList.contains('open'));
await page.getByText('Cotes').tap();
out.dims = await page.locator('#showd').isChecked();
await page.getByText('Grande penderie').tap();
await page.waitForTimeout(300);
for (const [word, value] of [['Transparent', 'see'], ['Plein', 'solid'], ['Masqué', 'hidden']]) {
  await page.getByText(word, { exact: true }).tap();
  out[word] = await page.locator(`input[name=rest][value=${value}]`).isChecked();
}
await page.getByRole('button', { name: 'Affichage' }).tap();
out.closed = !(await page.locator('#display').evaluate(e => e.classList.contains('open')));
out.errors = errors;
console.log(JSON.stringify(out));
await b.close();
