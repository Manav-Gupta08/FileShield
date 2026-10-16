# Threat Model

Assets: uploaded bytes, sanitized outputs, metadata/reports, credentials, session tokens, processing workers, database, queue and service secrets. Actors: malicious anonymous uploader, malicious account holder, automated bot, network attacker, compromised dependency or scanner.

Trust boundaries: browser/API, API/private storage, API/queue, worker/parser, parser/scanner, application/database, authenticated owner/object. Administrative access and host/kernel compromise are outside the application's enforceable guarantees.

| Threat | Scenario | Impact | Current mitigation | Test or release gate |
| --- | --- | --- | --- | --- |
| RCE / parser vulnerability | Crafted image/PDF exploits native/parser code | Worker code execution and secrets/files exposure | Separate child, timeout, container limits | Malformed image test; credential-free per-job sandbox remains required |
| Command injection | Filename/format contains shell metacharacters | OS command execution | Fixed subprocess argv, shell=False, no user codec flags | Invalid format/unknown parameter tests; external tools not exposed |
| Path traversal | Upload filename or archive entry includes ../, drive or absolute path | Read/write outside expected directory | UUID-only paths; filename labels; archives never extracted | Filename traversal and unsafe-entry tests |
| SSRF | Document URL points to internal service | Internal data access | No URL fetching in engine; worker internal-only network | Actual network denial test required before production |
| XXE | XML entity causes file reads or expansion | Secrets disclosure / DoS | Office/XML parser not exposed | Add defused XML tests when Office processing is implemented |
| XSS | Metadata or filename contains HTML/script | Browser credential/report theft | React text rendering, no dangerous HTML, CSP, attachment downloads | Browser malicious-label tests required |
| CSRF | Foreign page posts jobs with victim cookie | Unauthorized job or account mutation | SameSite Strict; exact Origin/Fetch-Site mutation checks | Cross-origin request test; trusted proxy deployment gate |
| IDOR | Attacker requests another owner's job/file UUID | Private report/file disclosure | Owner checks on read/download/delete; uniform 404 | Two-client report/download/delete test |
| Malware | Upload contains known malicious payload | Unsafe distribution | Required ClamAV input/output scan; fail closed on unavailable | Unavailable scanner test; actual EICAR integration gate |
| ZIP/decompression bomb | Small compressed upload expands massively | RAM/disk/CPU exhaustion | No extraction; size/count/ratio bounds, worker limits | ZIP bomb test; real bytes extraction test not applicable yet |
| Nested archives | Chains hide payload or multiply work | Hidden malware / resource exhaustion | Nested suffix warnings; depth zero | Nested ZIP report test; deeper interpretation unsupported |
| Image bomb | Tiny header declares enormous pixel count | Memory exhaustion | Pixel ceiling and Pillow bomb errors | Malformed image + pixel-bound tests |
| Large PDF / object graph | Huge page/object graph or costly compressed stream | CPU/RAM exhaustion | Page/object visits, parser child limits/timeout | PDF page-limit test; Linux limit behavior gate |
| API DoS | Repeated uploads or expensive auth requests | Availability loss | Request/files limit; job admission; category rate limits | Chunked body limit, request-size tests; deployment load test gate |
| Metadata leakage | GPS/author remains or report is logged | Personal privacy harm | Categorized findings; fresh pixels; owner-only reports; bounded retention | Author removal test; deep XMP/IPTC coverage remains open |
| Unauthorized access | Session guessing/theft or expired token reuse | Account/file access | Random high-entropy tokens, stored hashes, expiry, secure production cookie | Expired job test; session revocation tests |
| Storage leftovers | Crash before deletion or backup retains data | Privacy breach | Input cleanup, expiration sweeper, generated dirs | Timeout cleanup and expiry tests; orphan reconciliation/backups policy gate |
| Crypto tampering | Modified envelope or wrong password | Corrupt plaintext released | AES-GCM tag authenticated before output creation | Round-trip/tamper test |
| Supply chain | Dependency or base image compromised | Service compromise | Exact direct package pins, npm lock, audits, scheduled updates | pip-audit/npm audit; digest pinning/SBOM/Trivy gate |

Residual risk is explicit: a parser exploit still crosses into shared worker storage and credentials. Production must not rely on this baseline as a completed sandbox. No antivirus or test suite establishes universal safety.