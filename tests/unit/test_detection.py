import tempfile
from pathlib import Path

import pytest
from PIL import Image

from fileshield.detection import detect_file


def test_executable_disguised_as_image(tmp_path):
    path = tmp_path / "photo.jpg"
    path.write_bytes(b"MZ" + b"\x00" * 100)
    result = detect_file(str(path), declared_mime="image/jpeg")
    assert result["detected_mime"] == "application/x-dosexec"
    assert len(result["warnings"]) == 3
    assert result["parser_validated"] is False


def test_image_parser_validation(tmp_path):
    path = tmp_path / "image.png"
    Image.new("RGB", (8, 7)).save(path)
    result = detect_file(str(path))
    assert result["dimensions"] == [8, 7]
    assert result["parser_validated"] is True
    assert result["warnings"] == []


def test_truncated_image_is_rejected(tmp_path):
    path = tmp_path / "broken.png"
    path.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(OSError):
        detect_file(str(path))


def test_unknown_content_is_not_trusted(tmp_path):
    path = tmp_path / "photo.jpg"
    path.write_bytes(b"not an image")
    assert detect_file(str(path))["signature"] == "unknown"