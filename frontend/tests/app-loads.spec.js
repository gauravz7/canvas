import { test, expect } from '@playwright/test';

test('app loads and shows canvas', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Vibe | Multimodal Studio');
  await expect(page.getByRole('heading', { name: 'Canvas' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Run', exact: true })).toBeVisible();
});

test('sidebar navigation to saved canvas works', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Saved Canvas' }).click();
  await expect(page.getByText('Saved Workflows')).toBeVisible();
});

test('toolbar shows all node categories', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Inputs')).toBeVisible();
  await expect(page.getByText('Gemini', { exact: true })).toBeVisible();
  await expect(page.getByText('Voice & Music')).toBeVisible();
  await expect(page.getByText('Video Gen')).toBeVisible();
  await expect(page.getByText('Outputs')).toBeVisible();
});
