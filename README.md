# FileShield

A privacy-focused file analysis, sanitization, transformation, protection, and security platform.

**Goal:** Safely handle untrusted user-supplied files by analyzing their contents and metadata, identifying privacy/security risks, and securely sanitizing or transforming them.

## Development

This project is developed incrementally with a strong emphasis on **security**, **understanding**, and **learning**.

See [CHANGELOG.md](CHANGELOG.md) for detailed feature information.

## Requirements

- Python 3.8+
- No external dependencies (for Milestone 1)

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
