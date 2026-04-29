import { test, expect } from '@playwright/test';

test('workflow execution shows node status updates via SSE', async ({ page }) => {
  await page.goto('/');

  await page.route('**/api/workflow/execute/stream', async (route) => {
    const events = [
      `data: {"type":"node_started","node_id":"1"}\n\n`,
      `data: {"type":"node_completed","node_id":"1","result":{"node_id":"1","status":"completed","output":"Quantum bits dance strangely.","error":null}}\n\n`,
      `data: {"type":"node_started","node_id":"2"}\n\n`,
      `data: {"type":"node_completed","node_id":"2","result":{"node_id":"2","status":"completed","output":{"audio":{"url":"/api/media/test/audio/test.wav","mime_type":"audio/wav"}},"error":null}}\n\n`,
      `data: {"type":"node_started","node_id":"3"}\n\n`,
      `data: {"type":"node_completed","node_id":"3","result":{"node_id":"3","status":"completed","output":{"audio":{"url":"/api/media/test/audio/test.wav","mime_type":"audio/wav"}},"error":null}}\n\n`,
      `data: {"type":"workflow_completed"}\n\n`,
    ].join('');

    await route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: events,
    });
  });

  await page.getByRole('button', { name: 'Run', exact: true }).click();
  await page.waitForTimeout(2000);

  await expect(page.locator('text=completed').first()).toBeVisible();
});

test('error propagation shows skipped nodes', async ({ page }) => {
  await page.goto('/');

  await page.route('**/api/workflow/execute/stream', async (route) => {
    const events = [
      `data: {"type":"node_started","node_id":"1"}\n\n`,
      `data: {"type":"node_failed","node_id":"1","result":{"node_id":"1","status":"failed","output":null,"error":"Model not found"}}\n\n`,
      `data: {"type":"node_skipped","node_id":"2","reason":"Upstream node failed"}\n\n`,
      `data: {"type":"node_skipped","node_id":"3","reason":"Upstream node failed"}\n\n`,
      `data: {"type":"workflow_completed"}\n\n`,
    ].join('');

    await route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: events,
    });
  });

  await page.getByRole('button', { name: 'Run', exact: true }).click();
  await page.waitForTimeout(2000);

  await expect(page.locator('text=failed').first()).toBeVisible();
  await expect(page.locator('text=skipped').first()).toBeVisible();
  await expect(page.locator('text=Skipped: upstream node failed').first()).toBeVisible();
});
