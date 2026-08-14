import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

  await page.goto('http://localhost:5173/');
  // Wait a bit for React to render
  await page.waitForTimeout(2000);
  
  await page.screenshot({ path: 'screenshot.png' });
  const html = await page.content();
  console.log('HTML Length:', html.length);
  
  await browser.close();
})();
