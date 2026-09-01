import hashlib
import tempfile
import unittest
from pathlib import Path

from fileshield.hashing import compute_hashes


class TestComputeHashes(unittest.TestCase):
    def test_compute_hashes_basic(self):
        data = b"hello world"
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(data)
            tf.flush()
            temp_path = tf.name

        try:
            expected_sha256 = hashlib.sha256(data).hexdigest()
            expected_sha512 = hashlib.sha512(data).hexdigest()

            digests = compute_hashes(temp_path, algorithms=("sha256", "sha512"), chunk_size=4)

            self.assertEqual(digests["sha256"], expected_sha256)
            self.assertEqual(digests["sha512"], expected_sha512)
        finally:
            Path(temp_path).unlink()

    def test_compute_hashes_empty_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_path = tf.name

        try:
            expected_sha256 = hashlib.sha256(b"").hexdigest()
            expected_sha512 = hashlib.sha512(b"").hexdigest()

            digests = compute_hashes(temp_path, algorithms=("sha256", "sha512"))

            self.assertEqual(digests["sha256"], expected_sha256)
            self.assertEqual(digests["sha512"], expected_sha512)
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    unittest.main()
