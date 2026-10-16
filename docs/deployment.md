# Deployment and Local Operation

## Windows Development

Use Python 3.12+, `.venv`, the pinned requirements, and `pip install --no-deps -e .`. Run `scripts/start-dev.ps1` and `npm --prefix frontend run dev -- --port 5173`. Development uses SQLite and thread-dispatched child processes, disables antivirus explicitly, and binds to loopback. Use synthetic fixtures only.

On POSIX set `FILESHIELD_SECRET_KEY` using `secrets.token_hex(32)`, `FILESHIELD_ENV=development`, `REQUIRE_SCAN=false`, and `PUBLIC_ORIGIN=http://localhost:5173`; then run `uvicorn backend.app:app --host 127.0.0.1 --port 8000 --no-access-log`. Never print production keys into shared logs.

## Local Docker Trial

Create a local `.env` from `.env.example`. Generate independent random server key and database password; server key must be 64 hex characters. Database passwords placed in the interpolated connection URL must use URL-safe characters or correct URL encoding. Do not commit `.env` or secrets. Keep the default development mode and loopback-only port for a first trial.

```powershell
docker compose config --quiet
docker compose build
docker compose up -d
```

First-time ClamAV signature downloads can delay scanning. Until the scanner replies with a definitive clean status, required-scan jobs fail closed. API `/health` is liveness/configuration, not dependency readiness.

## Production Gates

This Compose file is a trial scaffold, not a complete secure production deployment. Start with `docs/release-checklist.md`. Implement a credential-free parser sandbox with only one job mount and an authenticated narrow result channel. Add reviewed SQL migrations and crash reconciliation. Use durable Redis where required and recover queued/processing jobs after outages.

Configure a real HTTPS ingress and `FILESHIELD_ENV=production`, `PUBLIC_ORIGIN=https://your-host`, `REQUIRE_SCAN=true`. `POSTGRES_PASSWORD` and `FILESHIELD_SECRET_KEY` must be managed as deployment secrets. The example currently injects values through environment variables; migrate to a secrets manager/mounted secret mechanism and avoid exposing `docker compose config` output containing secrets.

Initialize a new production schema explicitly with `docker compose run --rm backend python -c "from backend.database import initialize_database; initialize_database()"` after configuration/review and before starting production API traffic. Existing databases need migrations, not create_all as an upgrade policy.

Verify worker non-root identity, resource enforcement, read-only root, internal-only service ports, scanner engine/signatures/readiness, egress restrictions, same-origin cookies/CSRF, owner access, expiry, storage capacity, health probes and recovery. Vendor containers must be hardened using their documented supported users/permissions. Pin image digests after scanning. No elevated privileges are required by application code.

No Docker daemon was available during initial local verification, so image builds, Linux limits, PostgreSQL/Redis/Celery integration, Nginx routing and real ClamAV scans remain unverified until this trial runs.