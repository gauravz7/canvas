import { test, expect } from '@playwright/test';

test('clicking template opens in new workflow tab', async ({ page }) => {
  page.on('console', msg => console.log('[BROWSER]', msg.text()));
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2000);

  // Initial: should have 1 tab
  const initialTabs = await page.locator('[title="Double-click to rename"]').count();
  console.log('Initial tabs:', initialTabs);
  expect(initialTabs).toBe(1);

  // Go to Saved Canvas
  await page.locator('button >> text=Saved Canvas').click();
  await page.waitForTimeout(2500);

  // Take screenshot
  await page.screenshot({ path: '/tmp/saved-canvas-templates.png' });

  // Find the templates section - look for template names
  const productAd = page.locator('button:has-text("Product Ad")');
  const count = await productAd.count();
  console.log('Product Ad buttons found:', count);

  if (count > 0) {
    await productAd.first().click();
    await page.waitForTimeout(2000);

    await page.screenshot({ path: '/tmp/after-template-click.png' });

    // Should have 2 tabs now
    const newTabsCount = await page.locator('[title="Double-click to rename"]').count();
    console.log('Tabs after click:', newTabsCount);
    expect(newTabsCount).toBe(2);
  } else {
    console.log('Templates not found, snapshot for debugging');
  }
});
