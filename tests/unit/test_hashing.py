import hashlib
import tempfile
from pathlib import Path

from fileshield.hashing import compute_hashes


def test_compute_hashes_basic():
    data = b"hello world"
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(data)
        tf.flush()
        temp_path = tf.name

    try:
        expected_sha256 = hashlib.sha256(data).hexdigest()
        expected_sha512 = hashlib.sha512(data).hexdigest()

        digests = compute_hashes(temp_path, algorithms=("sha256", "sha512"), chunk_size=4)

        assert digests["sha256"] == expected_sha256
        assert digests["sha512"] == expected_sha512
    finally:
        Path(temp_path).unlink()


def test_compute_hashes_empty_file():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        temp_path = tf.name

    try:
        expected_sha256 = hashlib.sha256(b"").hexdigest()
        expected_sha512 = hashlib.sha512(b"").hexdigest()

        digests = compute_hashes(temp_path, algorithms=("sha256", "sha512"))

        assert digests["sha256"] == expected_sha256
        assert digests["sha512"] == expected_sha512
    finally:
        Path(temp_path).unlink()
