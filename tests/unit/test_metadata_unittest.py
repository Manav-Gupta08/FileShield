import tempfile
import unittest
from pathlib import Path

from fileshield.metadata import extract_image_exif

try:
    from PIL import Image
except Exception:
    Image = None


class TestImageMetadata(unittest.TestCase):
    def test_extract_exif_on_simple_jpeg(self):
        if Image is None:
            self.skipTest("Pillow not installed")

        # Create a small RGB JPEG without EXIF
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
            temp_path = tf.name
        try:
            img = Image.new('RGB', (10, 10), color='red')
            img.save(temp_path, format='JPEG')

            exif = extract_image_exif(temp_path)
            # No EXIF was written; expect empty dict
            self.assertIsInstance(exif, dict)
            self.assertEqual(len(exif), 0)
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    unittest.main()

