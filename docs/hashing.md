# Hashing and Integrity

`compute_hashes()` creates each selected fixed-length hashlib digest and updates them in a single streaming pass. Default algorithms are SHA-256 and SHA-512. Chunk sizes must be positive integers; empty algorithm lists and SHAKE-style variable-length digests are rejected.

The CLI can request MD5 for legacy compatibility using `--algorithms md5`. MD5 and SHA-1 must not be used for adversarial collision resistance, password storage, or a security identity. Hashing is not encryption: anyone with the file can calculate its digest.

API `hash` can accept `expected_sha256`; `compare` accepts exactly two files and compares SHA-256 digests. This is a strong practical integrity comparison, not a mathematical proof that a collision is impossible. Expected hashes must come from an independently trusted source.

Tests cover known vectors, empty files, small chunks, invalid chunks, and permission denial on non-root POSIX. Windows permission semantics differ, so that one test is skipped there.