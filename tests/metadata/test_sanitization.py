import pytest
from PIL import Image

from fileshield.images import image_metadata, transform_image


def test_sanitization_keeps_original_and_removes_author(tmp_path):
    original = tmp_path / "input.jpg"
    output = tmp_path / "input.cleaned.png"
    exif = Image.Exif()
    exif[315] = "Private author"
    Image.new("RGB", (16, 16)).save(original, exif=exif)
    unchanged = original.read_bytes()
    report = transform_image(str(original), str(output))
    assert "Artist" in report["removed_exif_fields"]
    assert image_metadata(str(output))["exif"] == {}
    assert original.read_bytes() == unchanged


def test_existing_output_cannot_be_overwritten(tmp_path):
    path = tmp_path / "image.png"
    Image.new("RGB", (8, 8)).save(path)
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        transform_image(str(path), str(path))
    assert path.read_bytes() == original


def test_oversized_requested_image_is_rejected(tmp_path):
    path = tmp_path / "image.png"
    Image.new("RGB", (8, 8)).save(path)
    with pytest.raises(ValueError):
        transform_image(str(path), str(tmp_path / "out.png"), width=100000, height=100000)


def test_multiframe_image_rejected(tmp_path):
    path = tmp_path / "frames.tiff"
    Image.new("RGB", (8, 8)).save(path, save_all=True, append_images=[Image.new("RGB", (8, 8))])
    with pytest.raises(ValueError, match="Multi-frame"):
        transform_image(str(path), str(tmp_path / "out.png"))