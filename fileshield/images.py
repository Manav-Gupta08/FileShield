"""Fresh-pixel image transformations with exclusive output creation."""

from pathlib import Path

from PIL import Image, ImageOps

from fileshield.detection import MAX_IMAGE_PIXELS, detect_file
from fileshield.metadata import classify_exif_privacy, extract_image_exif


FORMATS = {"jpeg": ("JPEG", ".jpg"), "png": ("PNG", ".png"), "webp": ("WEBP", ".webp"), "tiff": ("TIFF", ".tiff")}


def image_metadata(file_path: str) -> dict:
    detection = detect_file(file_path)
    if not detection["detected_mime"].startswith("image/"):
        raise ValueError("A supported image is required")
    exif = extract_image_exif(file_path)
    with Image.open(file_path) as image:
        containers = sorted(str(key) for key in image.info)
    return {"exif": exif, "containers": containers, "privacy": classify_exif_privacy(exif)}


def transform_image(file_path: str, output_path: str, output_format: str = "png",
                    width: int | None = None, height: int | None = None,
                    quality: int = 85, rotation: int = 0, crop: list[int] | None = None,
                    dpi: int | None = None) -> dict:
    if output_format not in FORMATS:
        raise ValueError("Unsupported output format")
    if not 1 <= quality <= 100 or rotation not in {0, 90, 180, 270}:
        raise ValueError("Invalid quality or rotation")
    if dpi is not None and not 36 <= dpi <= 1200:
        raise ValueError("DPI must be between 36 and 1200")
    if width is not None or height is not None:
        if width is None or height is None or min(width, height) < 1 or width * height > MAX_IMAGE_PIXELS:
            raise ValueError("Both dimensions must be positive and within the pixel limit")
    before = image_metadata(file_path)
    output = Path(output_path)
    with Image.open(file_path) as image:
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Multi-frame images are not supported; no silent frame loss")
        image.load()
        transformed = ImageOps.exif_transpose(image)
        if crop is not None:
            if len(crop) != 4:
                raise ValueError("Crop requires four coordinates")
            left, top, right, bottom = crop
            if not (0 <= left < right <= transformed.width and 0 <= top < bottom <= transformed.height):
                raise ValueError("Crop is outside image bounds")
            transformed = transformed.crop(tuple(crop))
        if width is not None:
            transformed.thumbnail((width, height), Image.Resampling.LANCZOS)
        if rotation:
            transformed = transformed.rotate(rotation, expand=True)
        mode = "RGB" if output_format == "jpeg" else "RGBA"
        pixels = transformed.convert(mode)
        clean = Image.new(mode, pixels.size)
        clean.paste(pixels)
        options = {"quality": quality} if output_format in {"jpeg", "webp"} else {}
        if dpi is not None and output_format != "webp":
            options["dpi"] = (dpi, dpi)
        with output.open("xb") as stream:
            try:
                clean.save(stream, format=FORMATS[output_format][0], **options)
            except BaseException:
                stream.close()
                output.unlink(missing_ok=True)
                raise
    try:
        after = image_metadata(str(output))
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"file": detect_file(str(output)), "before": before, "after": after,
            "removed_exif_fields": sorted(set(before["exif"]) - set(after["exif"])),
            "remaining_exif_fields": sorted(after["exif"]),
            "limitations": ["Visible identifying content remains", "Color profiles are discarded",
                            "No forensic erasure or universal metadata-free guarantee"]}