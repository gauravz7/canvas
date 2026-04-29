import { test, expect } from '@playwright/test';

test('/data/history.db no longer serves database', async ({ page }) => {
  const response = await page.goto('/data/history.db');
  const body = await response.text();
  expect(body).toContain('<!doctype html>');
  expect(body).not.toContain('SQLite');
});

test('path traversal returns 404 or SPA fallback', async ({ request }) => {
  const response = await request.get('/api/media/..%2F..%2F/etc/passwd.txt');
  expect(response.status()).toBe(404);
});

test('media endpoint rejects traversal in user_id', async ({ request }) => {
  const response = await request.get('/api/media/..%2F..%2Fetc/passwd/test.txt');
  expect(response.status()).toBe(404);
});

test('valid media endpoint returns file when it exists', async ({ request }) => {
  const response = await request.get('/api/media/nonexistent/audio/fake.wav');
  expect(response.status()).toBe(404);
});

test('XSS content renders as text, not HTML', async ({ page }) => {
  await page.goto('/');

  await page.route('**/api/workflow/execute/stream', async (route) => {
    const ssePayload = [
      `data: {"type":"node_started","node_id":"3"}\n\n`,
      `data: {"type":"node_completed","node_id":"3","result":{"node_id":"3","status":"completed","output":{"videos":[{"url":"<script>alert(1)</script>","mime_type":"video/mp4"}]},"error":null}}\n\n`,
      `data: {"type":"workflow_completed"}\n\n`,
    ].join('');

    await route.fulfill({
      status: 200,
      headers: { 'Content-Type': 'text/event-stream' },
      body: ssePayload,
    });
  });

  await page.getByRole('button', { name: 'Run' }).click();
  await page.waitForTimeout(2000);

  const scriptTags = await page.locator('script').count();
  const alertFired = await page.evaluate(() => window.__xssTriggered || false);
  expect(alertFired).toBe(false);
});
