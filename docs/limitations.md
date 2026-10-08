# Capability Matrix and Known Limits

| Specification area | Current baseline | Remaining work |
| --- | --- | --- |
| File information/hashes | CLI information, SHA-256/SHA-512, optional CLI MD5, API verify/compare | Separate hash/compare UI controls |
| Type verification | Selected signatures, filename/declared MIME comparison, image parser validation | libmagic, polyglots, full MIME aliases/OOXML/media detection |
| Image metadata | EXIF/GPS sub-IFDs, container key presence, explainable score | Full IPTC/XMP/ICC/MakerNote interpretation |
| Sanitization | Fresh-pixel image copy; before/after EXIF comparison | Comprehensive preflight preview and field-by-field explanations in UI |
| Public release | Type/hash/metadata/heuristic security report and scan status | Complete embedded-content detection and format-specific release checklist |
| Images | Four formats; engine/API resize/crop/rotate/quality/DPI; batch ZIP | UI crop/DPI controls, thumbnails presets, broader formats/animation |
| PDF | Basic metadata/security walker and conservative rewrite/merge/pages/rotate | Compress, render, image-PDF, broad content disarm and short known-password UI |
| Office/media | Not implemented | Bounded OOXML parsing/sanitization, FFmpeg and LibreOffice sandboxed adapters |
| Malware | ClamAV INSTREAM adapter, fail-closed required scans | Real scanner integration/readiness/freshness evidence |
| Archives | ZIP/TAR/GZIP inspection; no extraction | 7Z, full recursive content inspection, safe extraction |
| Storage/uploads | Generated paths, limits, ownership, expiry/delete | Orphan recovery, storage quotas, secure at-rest storage deployment |
| Async isolation | Child process timeout, POSIX limits, Celery/Compose scaffold | Credential-free per-job mount/network sandbox and integration verification |
| Accounts | Optional registration/login, Argon2id, revocable current session | API keys, presets, recovery, account deletion/export |
| Hardening | Header/rate/CSRF/schema controls; direct pins and npm lock | HTTPS ingress, full transitive lock, alerting, scans, independent review |

Metadata absence is not proof of privacy; MIME signatures are not full validation; antivirus can miss threats; deletion is not forensic erasure. Development on Windows intentionally lacks Linux resource/container enforcement. Shared worker credentials/mounts are the primary production isolation blocker.