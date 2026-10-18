// Load the public A1 mini firmware download page in headless Chromium and
// print every firmware link plus visible version/date text.
// Usage: NODE_PATH=$(npm root -g) node scripts/fetch_download_page.js [url]
const { chromium } = require('playwright');
const url = process.argv[2] || 'https://bambulab.com/en/support/firmware-download/a1-mini';
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(20000);
  console.log('TITLE', await page.title());
  const links = await page.$$eval('a', as => as.map(a => a.href).filter(h => /bblmw|\.zip|\.sig/.test(h)));
  for (const l of [...new Set(links)]) console.log('LINK', l);
  const html = await page.content();
  for (const m of new Set(html.match(/https?:\/\/public-cdn\.bblmw\.com[^"'\s<>\\]+/g) || [])) console.log('URL', m);
  await browser.close();
})();
