# Changelog

All notable changes to FileShield will be documented in this file.

## [0.1.0] - 2026-09-01

### Added - Milestone 1, Step 1

#### File Information Command
- Create fileshield Python package structure
- Implement `FileInformation` class to extract filesystem metadata
- Add CLI interface for `info` command: `python3 fileshield_cli.py info <file_path>`
- Support human-readable file size formatting (B, KB, MB, GB, TB)
- Include permission checking (readable/writable status)

#### Features
- Display filename, absolute path, and extension
- Show file timestamps: created, modified, accessed
- Validate file existence (reject nonexistent files)
- Validate file type (reject directories)
- Proper error handling with appropriate exit codes

#### Usage
```bash
python3 fileshield_cli.py info <file_path>
```

Example output includes:
- Filename
- Absolute path
- File size (human-readable and bytes)
- Extension
- Creation, modification, access timestamps
- Read/write permissions

### Unreleased

#### Added
- SHA-256 hashing support via `fileshield.hashing.compute_sha256`
- CLI command: `fileshield_cli.py hash <file_path>` — computes SHA-256 digest

Notes:
- Hashing is implemented in a memory-efficient, chunked reader to avoid loading large files into memory.

