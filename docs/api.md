# REST API v1

Base path `/api/v1`. Same-origin browser access uses an HttpOnly, SameSite=Strict session cookie. `POST /session` creates an anonymous owner if no valid session exists. Accounts are optional. Secure cookies are required in production.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | /health | Environment and whether antivirus is required; not dependency readiness |
| POST | /session | Anonymous session or existing authentication state |
| POST | /auth/register | Username/password registration, Argon2id, fresh session |
| POST | /auth/login | Generic credential failure, fresh session |
| POST | /auth/logout | Revoke current session |
| POST | /jobs/{operation} | Multipart files plus JSON options; returns 202 and job_id |
| GET | /jobs | Up to 50 unexpired jobs owned by the current session/account |
| GET | /jobs/{job_id} | Owner-only status/report; never internal paths |
| GET | /files/{job_id} | Owner-only completed output attachment |
| DELETE | /files/{job_id} | Remove completed/failed job files and report |

Operations: `analyze`, `release`, `metadata`, `sanitize`, `hash`, `compare`, `scan`, `images`, `batch`, `pdf`, `archives`, `protect`, `decrypt`. The report operations share a bounded analysis pipeline; naming `metadata` or `archives` does not create a different decoder pipeline. Single-file operations take one upload, compare exactly two, PDF/batch up to ten. Entire upload payload files may total at most 25 MiB.

Multipart fields: repeated `files`; optional string `options` containing a JSON object. Unknown fields/options are rejected. Options include `output_format`, `width`, `height`, `quality`, `rotation`, `crop`, `dpi`, `pages`, `password`, `expected_sha256`. Some options apply only to a specific operation; accepted but inapplicable options are ignored. JSON validation errors are intentionally summarized without echoing secrets.

```json
{"output_format":"webp","width":2048,"height":2048,"quality":85}
```

```json
{"job_id":"a9e055de-f073-4b9a-9b08-8ac52c5db054"}
```

Statuses: queued, processing, completed, failed. Report content is returned only to the owner. Invalid, expired and foreign identifiers return the same 404. Pending deletion returns 409. Size violations return 413; schema failures 422; rate/capacity limits 429; queue outages 503. OpenAPI is available at `/openapi.json`; interactive docs require a separate CSP policy and are not the frontend.

The specification's `/files/analyze`, `/images/resize`, and similar aliases are not implemented; use the unified versioned job endpoint. API keys, presets, account recovery, pagination beyond the latest 50 jobs, progress percentages and cancellation are roadmap features.