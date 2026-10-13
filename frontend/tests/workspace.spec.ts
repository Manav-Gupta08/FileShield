import { test, expect } from '@playwright/test';
import path from 'node:path';

test('upload, inspect, sanitize, download and responsive reports', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await expect(page.getByText('Workspace connected')).toBeVisible();
  const bitmap = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAAI0lEQVR4nGPU6w5nIAUwkaSaYVQDcYCJSHVwMKqBGEByKAEAcvQBMCK8LeoAAAAASUVORK5CYII=', 'base64');
  await page.locator('input[type=file]').setInputFiles({ name: 'synthetic-preview.png', mimeType: 'image/png', buffer: bitmap });
  await expect(page.getByAltText('Selected input preview')).toBeVisible();
  expect(await page.getByAltText('Selected input preview').evaluate(image => (image as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await page.getByRole('button', { name: 'Analyze file', exact: true }).click();
  await page.getByRole('button', { name: 'Sanitize for release', exact: true }).click();
  await expect(page.getByRole('link', { name: 'Download result' })).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText('image/png', { exact: true })).toBeVisible();
  const href = await page.getByRole('link', { name: 'Download result' }).getAttribute('href');
  const response = await page.request.get(href!);
  expect(response.status()).toBe(200);
  expect(response.headers()['content-disposition']).toContain('attachment');
  expect((await response.body()).length).toBeGreaterThan(0);
  await page.getByRole('tab', { name: 'Integrity', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Copy sha256' })).toBeEnabled();
  await page.getByRole('tab', { name: 'Findings', exact: true }).click();
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({ width, height: 1000 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    if (width !== 320) await page.screenshot({ path: path.resolve('../docs', `workspace-${width === 1440 ? 'desktop' : 'mobile'}.png`), fullPage: true });
  }
  await page.getByRole('button', { name: 'Delete files and report' }).click();
  await expect(page.getByRole('heading', { name: 'No report yet' })).toBeVisible();
  expect(errors).toEqual([]);
});