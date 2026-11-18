// Drives the prototype as a person would: from the settings it opens on, picks each kind of
// dimensions and each look for the rest by tapping its word, closes the settings, and checks the
// page answered each time.
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/trans/.claude/skills/mockups-before-code/tools/package.json');
const { chromium } = require('playwright');
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await (await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true })).newPage();
const errors = []; page.on('pageerror', e => errors.push(e.message));
await page.goto(pathToFileURL(path.resolve('play-C.html')).href);
await page.waitForSelector('html[data-ready="1"]');
const out = {};
out.open = await page.locator('#display').evaluate(e => e.classList.contains('open'));
for (const [word, value] of [['Positions', 'chain'], ['Masquées', 'none'], ['Tailles', 'part']]) {
  await page.getByText(word, { exact: true }).tap();
  out[word] = await page.locator(`input[name=dims][value=${value}]`).isChecked();
}
for (const [word, value] of [['Transparent', 'see'], ['Plein', 'solid'], ['Masqué', 'hidden']]) {
  await page.getByText(word, { exact: true }).tap();
  out[word] = await page.locator(`input[name=rest][value=${value}]`).isChecked();
}
await page.getByRole('button', { name: 'Affichage' }).tap();
out.closed = !(await page.locator('#display').evaluate(e => e.classList.contains('open')));
out.errors = errors;
console.log(JSON.stringify(out));
await b.close();
