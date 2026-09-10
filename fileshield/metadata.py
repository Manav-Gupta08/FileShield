"""Metadata extraction utilities for FileShield.

Current scope: image EXIF extraction (JPEG, TIFF where supported).

This module provides a single convenience function `extract_image_exif` that
returns a mapping of EXIF tag names to values. It uses Pillow (PIL) under the
hood. The function is defensive: it validates that the file exists and is a
file, and returns an empty dict when no EXIF is present.
"""

from pathlib import Path
from typing import Dict, Any

try:
    from PIL import Image, ExifTags
except Exception:  # pragma: no cover - Pillow may be missing in some dev setups
    Image = None
    ExifTags = None


def extract_image_exif(file_path: str) -> Dict[str, Any]:
    """Extract EXIF metadata from an image file.

    Args:
        file_path: Path to an image file (JPEG, TIFF where supported).

    Returns:
        Dictionary mapping EXIF tag names (e.g. 'DateTime', 'Make') to values.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path points to a directory.
        RuntimeError: If Pillow is not installed.
        OSError: If the file cannot be opened as an image.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

    if Image is None:
        raise RuntimeError("Pillow is required for EXIF extraction. Install with 'pip install Pillow'.")

    with Image.open(path) as img:
        # Some images expose EXIF via getexif (Pillow 6.0+) or _getexif()
        exif_data = None
        try:
            exif = img.getexif()
            if exif:
                exif_data = dict(exif)
        except Exception:
            # Fallback to _getexif for older Pillow versions
            try:
                raw = img._getexif()
                if raw:
                    exif_data = dict(raw)
            except Exception:
                exif_data = None

        if not exif_data:
            return {}

        # Map numeric EXIF tags to human-readable names where possible
        tag_map = {v: k for k, v in ExifTags.TAGS.items()} if ExifTags else {}

        parsed = {}
        for tag_num, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_num, str(tag_num)) if ExifTags else str(tag_num)
            parsed[tag_name] = value

        return parsed


def classify_exif_privacy(exif: Dict[str, Any]) -> Dict[str, Any]:
    """Classify EXIF fields by privacy relevance.

    Returns a structure with counts and lists for HIGH/MEDIUM/LOW sensitivity fields.

    Heuristics (initial):
    - HIGH: GPS, GPSLatitude, GPSLongitude, GPSInfo
    - MEDIUM: Camera make/model, Artist, Software, ImageUniqueID
    - LOW: DateTime, Orientation, ExifImageWidth/Height
    """
    if not exif:
        return {"score": 0, "high": [], "medium": [], "low": [], "details": {}}

    high_keys = {"gpsinfo", "gpslatitude", "gpslongitude", "gps"}
    medium_keys = {"make", "model", "artist", "software", "imageuniqueid", "ownername"}
    low_keys = {"datetime", "orientation", "exifimagewidth", "exifimageheight", "datetimeoriginal"}

    found_high = []
    found_medium = []
    found_low = []
    details = {}

    for k, v in exif.items():
        key = str(k).lower()
        details[key] = v
        if any(h in key for h in high_keys):
            found_high.append(key)
        elif any(m in key for m in medium_keys):
            found_medium.append(key)
        elif any(l in key for l in low_keys):
            found_low.append(key)

    # Simple explainable score: HIGH=50, MED=20, LOW=5 per field, capped at 100
    score = min(100, 50 * len(found_high) + 20 * len(found_medium) + 5 * len(found_low))

    return {"score": score, "high": found_high, "medium": found_medium, "low": found_low, "details": details}
