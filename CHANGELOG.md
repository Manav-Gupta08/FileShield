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
SHA-256 and SHA-512 hashing support via `fileshield.hashing.compute_hashes`
CLI command: `fileshield_cli.py hash <file_path>` — computes SHA-256 and SHA-512 digests

Notes:

#### Added
- Image EXIF extraction via `fileshield.metadata.extract_image_exif`
- Added `Pillow` to `requirements.txt` for image metadata support
- Unit test for basic EXIF extraction: `tests/unit/test_metadata_unittest.py`

#### Changed
- Added `requirements.txt` with test dependencies (pytest)
- Added GitHub Actions workflow to run unit tests (`.github/workflows/python-ci.yml`)
- CLI: Added `--algorithms` and `--json` options for `hash` command

#### Added
- Unit tests for `compute_hashes()` under `tests/unit/`


