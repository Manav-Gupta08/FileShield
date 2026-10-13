import { defineConfig } from '@playwright/test';
import { randomBytes } from 'node:crypto';
import path from 'node:path';

const python = path.resolve(process.platform === 'win32' ? '../.venv/Scripts/python.exe' : '../.venv/bin/python');

export default defineConfig({
  testDir: './tests',
  workers: 1,
  timeout: 60_000,
  use: { baseURL: 'http://localhost:5173', browserName: 'chromium' },
  webServer: [
    {
      command: `"${python}" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --no-access-log`,
      cwd: path.resolve('..'),
      url: 'http://127.0.0.1:8000/api/v1/health',
      reuseExistingServer: !process.env.CI,
      env: {
        FILESHIELD_ENV: 'development', REQUIRE_SCAN: 'false', REDIS_URL: '',
        FILESHIELD_SECRET_KEY: randomBytes(32).toString('hex'), PUBLIC_ORIGIN: 'http://localhost:5173',
        DATABASE_URL: 'sqlite:///./temp/browser-tests.db', STORAGE_ROOT: './temp/browser-jobs',
      },
    },
    {
      command: 'npm run dev -- --port 5173 --strictPort',
      url: 'http://localhost:5173', reuseExistingServer: !process.env.CI,
    },
  ],
});