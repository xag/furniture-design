// Back inside the app: a parent page that, like Soban's sheet, pushes a history step when it opens
// the 3D view and closes it on popstate (app.js: the sheet's `closing` flag and history.back()).
// The view adds no step of its own, so with the display settings open, one Back closes the view, and
// the app's own Close (history.back() once) leaves the history as it found it.
import path from 'node:path';
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/trans/.claude/skills/mockups-before-code/tools/package.json');
const { chromium } = require('playwright');
const dir = path.resolve('states');
fs.writeFileSync(path.join(dir, '_parent.html'), `<!doctype html><body style="margin:0">
<div id="sheet"><iframe id="f" src="A-s01-rest.html" style="width:390px;height:780px;border:0"></iframe></div>
<script>history.pushState({sheet:1}, ''); window.shut = 0; window.depth = history.length;
addEventListener('popstate', () => { window.shut++; document.getElementById('sheet').hidden = true; });</script></body>`);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await (await b.newContext({ viewport: { width: 390, height: 780 } })).newPage();
await page.goto(pathToFileURL(path.join(dir, '_parent.html')).href);
await page.frame({ url: /A-s01-rest/ }).waitForSelector('html[data-ready="1"]');
const f = page.frameLocator('#f');
await f.locator('#opts').click();
const opened = await f.locator('#display').evaluate(e => e.classList.contains('open'));
const stepsAdded = await page.evaluate(() => history.length - window.depth);
await page.evaluate(() => history.back());
await page.waitForTimeout(300);
const viewClosedByOneBack = await page.evaluate(() => window.shut);
console.log(JSON.stringify({ opened, stepsAdded, viewClosedByOneBack }));
await b.close();
