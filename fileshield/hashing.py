"""Hashing utilities for FileShield.

Provide memory-efficient functions to compute cryptographic hashes for files.
"""

import hashlib
from pathlib import Path


def compute_hashes(file_path: str, algorithms=("sha256", "sha512"), chunk_size: int = 8192) -> dict:
    """Compute multiple cryptographic digests for a file in a single pass.

    This reads the file once and updates all requested hash objects per chunk,
    avoiding multiple reads for multiple algorithms.

    Args:
        file_path: Path to the file to hash.
        algorithms: Iterable of algorithm names supported by hashlib (e.g. 'sha256', 'sha512').
        chunk_size: Number of bytes to read per iteration.

    Returns:
        Dictionary mapping algorithm name to hex digest.
    """
    path = Path(file_path)

    # Initialize hash objects
    hashers = {name: hashlib.new(name) for name in algorithms}

    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            for h in hashers.values():
                h.update(chunk)

    return {name: h.hexdigest() for name, h in hashers.items()}


def compute_sha256(file_path: str, chunk_size: int = 8192) -> str:
    """Backward-compatible helper that returns only the SHA-256 digest."""
    return compute_hashes(file_path, algorithms=("sha256",), chunk_size=chunk_size)["sha256"]
