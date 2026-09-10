# FileShield

A privacy-focused file analysis, sanitization, transformation, protection, and security platform.

**Goal:** Safely handle untrusted user-supplied files by analyzing their contents and metadata, identifying privacy/security risks, and securely sanitizing or transforming them.

## Development

This project is developed incrementally with a strong emphasis on **security**, **understanding**, and **learning**.

See [CHANGELOG.md](CHANGELOG.md) for detailed feature information.

## Requirements

- Python 3.8+

For development and running the tests, install the development requirements:

```bash
pip install --user -r requirements.txt
```

Note: `requirements.txt` currently lists `pytest` so tests can be executed; the code itself uses only the Python standard library for Milestone 1.

## Quick Start

```bash
# Display basic file information
python3 fileshield_cli.py info <file_path>
```

Example:
```bash
python3 fileshield_cli.py info /etc/hostname
```

## Project Status

- **Current Milestone:** Milestone 1 - Python File Engine
- **Current Step:** Step 1 - Basic file information command
- **Next:** SHA-256 hashing, MIME detection, magic-byte detection

## Testing & Continuous Integration

Unit tests are in the `tests/` directory. Run them locally with Python's unittest runner (no external deps required):

```bash
# from repo root
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py" -v
```

Alternatively, install `pytest` and run:

```bash
pip install --user pytest
PYTHONPATH=. pytest -q
```

A GitHub Actions workflow has been added at `.github/workflows/python-ci.yml` to run the tests on push and pull requests.
