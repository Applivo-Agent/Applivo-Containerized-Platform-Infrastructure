const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://internshala.com/internship/detail/work-from-home-fundraising-internship-at-queens-of-change-foundation1777548944');
  await page.waitForLoadState('networkidle');
  
  const applyBtnHTML = await page.evaluate(() => {
    const btn = document.querySelector('.top_apply_now_cta, a:has-text("Apply now")');
    return btn ? btn.outerHTML : 'Not found';
  });
  console.log('Apply button HTML:', applyBtnHTML);
  
  await browser.close();
})();
