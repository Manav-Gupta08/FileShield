# Security Controls and Release Policy

Treat every upload as hostile. No filename, extension, declared MIME, successful parse, hash match, EXIF score or antivirus response is independently a safety guarantee.

Current bounds: 26 MiB HTTP body, 25 MiB aggregate uploaded file bytes, 10 multipart files, 20 million image pixels, 200 PDF pages, 10,000 PDF object visits, 1,000 archive entries, 100 MiB declared expanded archive bytes, 100:1 relevant expansion ratio, 25 MiB downloadable output, 256 KiB stored JSON report, 10 pending jobs. Default child timeout is 60 seconds, configurable 1-300. Retention defaults to one hour, configurable 60 seconds to 24 hours.

Rate limits use fixed windows: 120 requests/IP/minute, 10 session creations/IP/minute, 5 authentication attempts/IP/minute, 5 anonymous or 20 authenticated job submissions/owner/minute. Redis provides shared atomic counting; development has bounded process-local accounting only. Proxy client identity is not yet safely forwarded, so Compose requests share the proxy IP quota; configure a trusted ingress identity model before public operation.

Production configuration requires HTTPS origin, PostgreSQL, Redis, scanning enabled and an explicit 32-byte job-parameter key. The app cannot prove that the ingress really terminates HTTPS: that is an operator responsibility. Access logs are disabled in starter/containers to reduce IP/URL retention.

HTTP headers: `nosniff` prevents MIME guessing; `no-referrer` limits URL disclosure; Permissions-Policy denies camera/microphone/geolocation; `frame-ancestors 'none'` prevents framing; API CSP disallows active content; frontend CSP permits bundled same-origin scripts and blob image previews. Secure/HttpOnly/SameSite=Strict cookies reduce token exposure and cross-site use. HSTS is emitted in production, after real HTTPS is configured. Cache-Control no-store protects API reports and downloads from ordinary browser caches.

Logs contain event names/job identifiers, not passwords, uploaded bytes, metadata dumps or internal paths. Parser stdout/stderr is suppressed by orchestration to prevent accidental disclosure. This also limits debugging evidence; structured categories need expansion without including sensitive payloads. IP identities are used transiently or hashed into short-lived Redis keys, not deliberately retained in event logs.

Compose hardens application containers using non-root users, read-only roots, capability drops, no-new-privileges, temporary storage, CPU/memory/PID limits and internal service networks. Vendor PostgreSQL/ClamAV images require additional image-specific non-root/capability validation. ClamAV alone has an update-egress network. Tagged base images are not immutable digests yet.

**Release blockers:** child inherits credentials/shared mounts, unverified Docker execution, no database migration framework, queue/reconciliation gaps, unverified scanner signatures/readiness, no strong ingress identity policy or load test, no independent security review. See release checklist. Do not deploy as a public hostile-file service until these gates are closed.