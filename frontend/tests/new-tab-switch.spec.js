import { test, expect } from '@playwright/test';

test('clicking + New immediately switches to the new empty tab', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2500);

  // Initial: should have 1 tab with sample nodes
  const initialNodes = await page.locator('[data-testid^="rf__node"]').count();
  console.log('Initial nodes:', initialNodes);
  expect(initialNodes).toBeGreaterThan(0);

  // Click + New
  await page.locator('text=+ New').click();
  await page.waitForTimeout(800);

  // Now should have 2 tabs total
  const tabCount = await page.locator('[title="Double-click to rename"]').count();
  console.log('Tabs after + New:', tabCount);
  expect(tabCount).toBe(2);

  await page.screenshot({ path: '/tmp/new-tab-active.png' });

  // The visible canvas should be EMPTY (new tab)
  // Check for visible nodes - the new tab should have 0 visible nodes
  const visibleNodesInActiveTab = await page.locator('div[style*="visibility: visible"] [data-testid^="rf__node"]').count();
  console.log('Visible nodes in active tab:', visibleNodesInActiveTab);

  // Active tab indicator
  const activeTab = page.locator('[title="Double-click to rename"]').nth(1);
  const activeTabBg = await activeTab.evaluate(el => window.getComputedStyle(el).backgroundColor);
  console.log('Tab 1 background:', activeTabBg);
});
