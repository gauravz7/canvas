import { test, expect } from '@playwright/test';

test('workflow tabs are visible and functional', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2000);

  // Check tab bar exists with "Untitled Workflow" and "+ New"
  await expect(page.locator('text=Untitled Workflow').first()).toBeVisible();
  await expect(page.locator('text=+ New')).toBeVisible();

  // Click "+ New" to add a second tab
  await page.locator('text=+ New').click();
  await page.waitForTimeout(500);

  // Should now have 2 "Untitled Workflow" tabs
  const tabs = page.locator('[title="Double-click to rename"]');
  expect(await tabs.count()).toBe(2);

  await page.screenshot({ path: '/tmp/tabs-two.png' });
});

test('double-click to rename tab', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2000);

  // Double-click the tab to rename
  const tab = page.locator('[title="Double-click to rename"]').first();
  await tab.dblclick();
  await page.waitForTimeout(300);

  // Should show an input field
  const input = page.locator('[title="Double-click to rename"] input');
  await expect(input).toBeVisible();

  // Type new name
  await input.fill('My Workflow');
  await input.press('Enter');
  await page.waitForTimeout(300);

  // Tab should now show "My Workflow"
  await expect(page.locator('text=My Workflow')).toBeVisible();

  await page.screenshot({ path: '/tmp/tabs-renamed.png' });
});

test('tab state preserved when switching sidebar tabs', async ({ page }) => {
  await page.goto('http://localhost:5175');
  await page.waitForTimeout(2000);

  // The sample workflow should have nodes
  const nodesBefore = await page.locator('[data-testid^="rf__node"]').count();
  expect(nodesBefore).toBeGreaterThan(0);

  // Switch to History tab
  await page.locator('button >> text=History').click();
  await page.waitForTimeout(500);

  // Switch back to Canvas
  await page.locator('button >> text=Canvas').first().click();
  await page.waitForTimeout(1000);

  // Nodes should still be there
  const nodesAfter = await page.locator('[data-testid^="rf__node"]').count();
  expect(nodesAfter).toBe(nodesBefore);
});
