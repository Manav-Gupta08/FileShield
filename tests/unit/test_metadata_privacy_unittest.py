import unittest
from fileshield.metadata import classify_exif_privacy


class TestExifPrivacy(unittest.TestCase):
    def test_empty_exif(self):
        res = classify_exif_privacy({})
        self.assertEqual(res["score"], 0)
        self.assertEqual(res["high"], [])

    def test_gps_and_camera(self):
        exif = {
            "GPSInfo": {"GPSLatitude": (1, 2), "GPSLongitude": (3, 4)},
            "Make": "Canon",
            "Model": "EOS",
            "DateTime": "2026:09:10 12:00:00",
        }
        res = classify_exif_privacy(exif)
        self.assertIn("gpsinfo", res["high"])
        self.assertIn("make", res["medium"])
        self.assertGreater(res["score"], 0)


if __name__ == "__main__":
    unittest.main()
