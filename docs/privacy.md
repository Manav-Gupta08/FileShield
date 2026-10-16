# Privacy and Retention

Processing is intended to be local/self-hosted. No upload is intentionally sent to a third-party analysis API. ClamAV may download signature updates; this is distinct from sending user files to a cloud scanner. Browser fonts/icons/scripts are bundled or local rather than remote analytics resources.

Stored temporarily: generated job IDs, owner ID, sanitized display filenames, declared MIME labels, encrypted operation parameters, status, bounded metadata/security reports, input bytes during processing, and output bytes until deletion/expiration. Accounts store username and Argon2id password hashes. Sessions store random-token hashes, owners and expiry. Redis contains queue IDs and short-lived rate counters.

Inputs are normally unlinked after processing. Outputs/reports default to one-hour retention. API access is denied once expiry passes; the sweeper normally runs every 30 seconds, with additional grace for active jobs. Manual deletion removes completed/failed job directories and reports. Temporary multipart files are closed by the request form context manager.

Deletion means ordinary filesystem unlink/directory removal and SQL row removal, not guaranteed forensic erasure. SSD wear leveling, journaling, snapshots, backups, memory, crash dumps and database WAL can retain data. Operators must define encrypted storage, snapshot/backups, log retention and key management policies. Orphan directory recovery after abnormal crash remains a release gate.

User accounts are not deleted by file-retention cleanup. There is no account deletion/export endpoint yet; public deployment requires those policy decisions and controls. Signing in changes owner identity and does not transfer anonymous jobs automatically; anonymous reports disappear from that account view but still expire.

The ignored learning guide is local-only by default. Do not insert real user files, keys or metadata into screenshots, tests, documentation or source control. A privacy notice for a hosted service must state operator identity, jurisdiction, lawful basis, retention, subprocessors and rights; this engineering note is not legal advice or a complete policy.