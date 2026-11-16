// Back inside the app: a parent page that, like Soban's sheet, pushes a history step when it opens
// the 3D view and closes it on popstate. Opening the display settings then pressing Back must close
// the settings and leave the view open; a second Back closes the view.
import path from 'node:path';
import fs from 'node:fs';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire('C:/Users/trans/.claude/skills/mockups-before-code/tools/package.json');
const { chromium } = require('playwright');
const dir = path.resolve('states');
fs.writeFileSync(path.join(dir, '_parent.html'), `<!doctype html><body style="margin:0">
<div id="sheet"><iframe id="f" src="A-s01-rest.html" style="width:390px;height:780px;border:0"></iframe></div>
<script>history.pushState({sheet:1}, ''); window.shut = 0;
addEventListener('popstate', () => { window.shut++; document.getElementById('sheet').hidden = true; });</script></body>`);
const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await (await b.newContext({ viewport: { width: 390, height: 780 } })).newPage();
await page.goto(pathToFileURL(path.join(dir, '_parent.html')).href);
const f = page.frameLocator('#f');
await page.frame({ url: /A-s01-rest/ }).waitForSelector('html[data-ready="1"]');
await f.locator('#layers').click();
const open1 = await f.locator('#display').evaluate(e => e.classList.contains('open'));
await page.evaluate(() => history.back());
await page.waitForTimeout(300);
const open2 = await f.locator('#display').evaluate(e => e.classList.contains('open'));
const parentClosed1 = await page.evaluate(() => window.shut);
await f.locator('#layers').click();
await f.locator('#close').click();
await page.waitForTimeout(300);
const parentClosed2 = await page.evaluate(() => window.shut);
const open3 = await f.locator('#display').evaluate(e => e.classList.contains('open'));
await page.evaluate(() => history.back()); await page.waitForTimeout(300);
const parentClosed3 = await page.evaluate(() => window.shut);
console.log(JSON.stringify({ openedByButton: open1, openAfterBack: open2, viewClosedByThatBack: parentClosed1,
  viewClosedByCloseButton: parentClosed2, openAfterClose: open3, viewClosedBySecondBack: parentClosed3 }));
await b.close();
