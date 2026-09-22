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

#### Milestone 2 (in progress)

- Image EXIF extraction: `fileshield.metadata.extract_image_exif`
	- Basic EXIF extraction for JPEG/TIFF using Pillow.
	- Returns a mapping of EXIF tag names to values.
	- Adds defensive validation for file existence and type.
	- Unit test: `tests/unit/test_metadata_unittest.py` (creates a small JPEG and checks for no EXIF).
	- `Pillow` added to `requirements.txt` to support image metadata extraction.

#### Milestone 1 (completed work since 0.1.0)

- Step 1: Basic file information command
	- `fileshield_cli.py info <file_path>` — shows filename, absolute path, size, extension, timestamps, permissions.

- Step 2: File hashing and verification
	- `fileshield.hashing.compute_hashes()` — compute multiple digests in a single pass (supports `sha256`, `sha512` by default).
	- `fileshield.hashing.compute_sha256()` — compatibility helper.
	- `fileshield_cli.py hash <file_path>` — CLI command to compute hashes.
	- CLI options: `--algorithms` (comma-separated, validated) and `--json` output for machine-readable results.
	- Permission error handling added to CLI commands (friendly messages for unreadable files).
	- Unit tests for hashing: `tests/unit/test_hashing_unittest.py` and `tests/unit/test_hashing.py` (basic, empty-file, unreadable-file tests).

- Infrastructure and docs
	- GitHub Actions workflow `.github/workflows/python-ci.yml` to run unit tests on push/PR.
	- `requirements.txt` added (lists `pytest`, `Pillow`).
	- `README.md` updated with test and CI instructions and example metadata usage.

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


