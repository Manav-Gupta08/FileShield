# FileShield

A self-hosted file privacy workspace: identify files, inspect privacy risks, create sanitized copies, verify integrity, and protect files with authenticated encryption.

**Status: tested development baseline, not a certified production service.** The complete product specification is a roadmap. Read [limitations](docs/limitations.md) and [release gates](docs/release-checklist.md) before accepting hostile public uploads.

## Available Workflows

- CLI file information, signature/MIME evidence, SHA-256/SHA-512, image EXIF, privacy classification, sanitization, archive inspection, encryption/decryption.
- React/TypeScript upload workspace, categorized EXIF findings, risk score, output downloads, history, account registration/login, anonymous sessions.
- FastAPI versioned asynchronous jobs, ownership checks, bounded uploads, generated storage paths, retention, rate limits, and security headers.
- JPEG/PNG/WebP/TIFF fresh-pixel sanitization and conversion; bounded resize, crop, rotation, quality and DPI through the engine/API; batch ZIP output.
- Conservative PDF metadata rewriting, merge/extract/reorder/rotate through page selection. Active, annotated, embedded, form, or signed PDFs are refused for rewriting.
- ZIP/TAR/GZIP inspection without extraction; ClamAV INSTREAM adapter; Scrypt + AES-256-GCM containers.
- Redis/Celery/PostgreSQL and non-root application container scaffolding. The Docker stack still requires execution-based verification.

## Local Setup (Windows PowerShell)

Python **3.12+** and Node **24 LTS** are required. Python 3.12 is locally verified; later versions require CI evidence. Python 3.8-3.11 are no longer supported.

```powershell
py -3.12 -m venv .venv
& ./.venv/Scripts/python.exe -m pip install --upgrade pip
& ./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
& ./.venv/Scripts/python.exe -m pip install --no-deps -e .
npm --prefix frontend ci
& ./.venv/Scripts/python.exe -m pytest -q
```

Start the API and frontend in separate terminals:

```powershell
./scripts/start-dev.ps1
```

```powershell
npm --prefix frontend run dev -- --port 5173
```

Open http://localhost:5173. API OpenAPI schema: http://127.0.0.1:8000/openapi.json. Development disables antivirus explicitly and is only for non-sensitive test fixtures. Local subprocesses are **not** a Windows sandbox. The starter generates an ephemeral job-parameter key; old jobs cannot resume after changing that key.

On POSIX, create `.venv` using `python3.12 -m venv .venv`, use `.venv/bin/python`, and set environment variables listed in [deployment](docs/deployment.md). Do not expose the local development server publicly.

## CLI

```powershell
& ./.venv/Scripts/python.exe fileshield_cli.py info photo.jpg
& ./.venv/Scripts/python.exe fileshield_cli.py hash photo.jpg --json
& ./.venv/Scripts/python.exe fileshield_cli.py metadata photo.jpg
& ./.venv/Scripts/python.exe fileshield_cli.py sanitize photo.jpg
& ./.venv/Scripts/python.exe fileshield_cli.py archives bundle.zip
& ./.venv/Scripts/python.exe fileshield_cli.py protect report.pdf --output report.fshield
```

Sanitization defaults to `photo.cleaned.png`; outputs are created exclusively and originals are not overwritten. Encryption passwords are prompted, not passed on the command line. CLI processing does not automatically scan or sandbox input.

## Documentation

- [Architecture](docs/architecture.md), [API](docs/api.md), [Deployment](docs/deployment.md)
- [Threat model](docs/threat-model.md), [Security](docs/security.md), [Privacy](docs/privacy.md)
- [Metadata](docs/metadata.md), [Sanitization](docs/sanitization.md), [Scoring](docs/scoring.md)
- [File types](docs/file-types.md), [Hashing](docs/hashing.md), [Archives](docs/archives.md), [PDF](docs/pdf.md), [Protection](docs/protection.md)
- [Limitations](docs/limitations.md), [Performance](docs/performance.md), [Dependency policy](docs/dependencies.md), [Release checklist](docs/release-checklist.md)

The local `PROJECT_PHASE_GUIDE.md` contains the teaching walkthrough and seven-day, 70-commit command schedule. It is deliberately ignored and excluded from container builds.

## Verification

```powershell
./scripts/check-security.ps1
& ./frontend/node_modules/.bin/playwright.cmd install chromium
npm --prefix frontend run test:browser
docker compose config --quiet --no-interpolate
```

The browser test uses a synthetic PNG and checks upload, analysis, sanitization, download, deletion and layout widths of 1440, 390 and 320 pixels. It captures [desktop](docs/workspace-desktop.png) and [mobile](docs/workspace-mobile.png) reports. This is not a complete accessibility audit.

Use pytest as the authoritative runner: the old unittest discovery command could miss tests in non-package subdirectories. Audit results are time-dependent. Do not interpret green tests, a zero EXIF score, or an antivirus clean response as proof of safety.
