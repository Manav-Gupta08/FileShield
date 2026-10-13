# FileShield Workspace

React 19 and TypeScript, built by Vite. Run `npm ci`, then `npm run dev -- --port 5173`. The development proxy sends `/api` to loopback port 8000. No direct browser access to PostgreSQL/Redis/ClamAV exists.

`src/api.ts` centralizes same-origin requests and errors; `App.tsx` handles uploads, job polling, reports, conversion controls and accounts; `styles.css` provides responsive operational layouts. File preview URLs are local blobs and are revoked when input changes. Metadata is rendered as text, never HTML.

Build/type check: `npm run build`. The Docker image builds static assets and serves them through unprivileged Nginx. No remote fonts or analytics are required. Browser screenshots and security tests are described in `../docs/accessibility.md` and the release checklist.