# Archive Security

The analyzer never extracts files. ZIP entries are inspected for file count, declared sizes, per-entry expansion ratio, duplicate names, encryption, symlinks, nested archives and executable/script suffixes. TAR is processed as a stream of headers and special members are flagged. GZIP is decompressed in bounded chunks to count expanded bytes but its payload is not recursively interpreted.

Limits: 25 MiB input, 100 MiB aggregate uncompressed bytes, 1,000 entries, 100:1 per-ZIP-entry/GZIP expansion ratio, and maximum recursive depth zero. The API worker also supplies an overall wall-clock timeout. These are fixed conservative engine constants, not a fully environment-configurable archive policy yet.

Unsafe names include absolute POSIX paths, Windows drive paths, backslash traversal, `..` components, NUL bytes, alternate-data-stream colons and excessively long names. Symlinks, hardlinks, devices and other special entries must never be followed by a future extractor.

ZIP sizes are central-directory declarations, not verified streamed member sizes. Payloads are not individually decompressed or scanned. TAR/GZIP concatenation, 7Z, encrypted archives, deep nesting analysis and safe extraction remain unsupported. Whole-archive antivirus scanning does not guarantee every embedded member was inspected.

An extraction feature must independently enforce actual bytes written, count, ratio, nesting and wall time, reject links/devices, use directory-relative file creation with no symlink following, and prove that every destination remains below its generated directory.