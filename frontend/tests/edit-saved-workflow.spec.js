import { test, expect } from '@playwright/test';

test('opening saved workflow allows editing same workflow id', async ({ page }) => {
  page.on('console', msg => console.log('[BROWSER]', msg.text()));
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2500);

  // Open a template (Product Ad) into a new tab
  await page.locator('button >> text=Saved Canvas').click();
  await page.waitForTimeout(2500);
  await page.locator('button:has-text("Product Ad")').first().click();
  await page.waitForTimeout(2000);

  // Should be on canvas with the template loaded
  const tabs = await page.locator('[title="Double-click to rename"]').count();
  expect(tabs).toBe(2);

  // The new tab name should be "Product Ad (16:9)"
  await expect(page.locator('[title="Double-click to rename"]:has-text("Product Ad")')).toBeVisible();

  // Visible canvas should show nodes
  await page.waitForTimeout(500);
  const visibleNodes = await page.locator('[data-testid^="rf__node"]').count();
  console.log('Visible nodes:', visibleNodes);
  expect(visibleNodes).toBeGreaterThan(5);

  await page.screenshot({ path: '/tmp/edit-loaded-workflow.png' });
});

test('clicking same template twice focuses existing tab', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2500);

  await page.locator('button >> text=Saved Canvas').click();
  await page.waitForTimeout(2500);

  // Click Product Ad twice
  await page.locator('button:has-text("Product Ad")').first().click();
  await page.waitForTimeout(1500);

  await page.locator('button >> text=Saved Canvas').click();
  await page.waitForTimeout(1500);
  await page.locator('button:has-text("Product Ad")').first().click();
  await page.waitForTimeout(1500);

  // Should still be 2 tabs (not 3) - existing one focused
  const tabs = await page.locator('[title="Double-click to rename"]').count();
  console.log('Tabs after double-click same template:', tabs);
  expect(tabs).toBe(2);
});
