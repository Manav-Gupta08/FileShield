"""Hashing utilities for FileShield.

Provide memory-efficient functions to compute cryptographic hashes for files.
"""

import hashlib
from pathlib import Path


def compute_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Compute SHA-256 digest for the given file.

    Reads the file in chunks to avoid loading large files into memory.

    Args:
        file_path: Path to the file to hash.
        chunk_size: Number of bytes to read per iteration.

    Returns:
        Hexadecimal SHA-256 digest string.
    """
    path = Path(file_path)
    hasher = hashlib.sha256()

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
