// Render every NAME_WxH.html under a folder to NAME_WxH.png (needs Playwright).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = process.argv[2];
const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
  e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.html') ? [path.join(d, e.name)] : []);
(async () => {
  const b = await chromium.launch();
  for (const f of walk(dir)) {
    const [, w, h] = f.match(/_(\d+)x(\d+)\.html$/).map(Number);
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.resolve(f));
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(300);
    await p.screenshot({ path: f.replace(/\.html$/, '.png') });
    await p.close();
  }
  await b.close();
})();
