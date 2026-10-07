"""Bounded content identification; a signature is evidence, not a safety verdict."""

import mimetypes
import warnings
from pathlib import Path

from PIL import Image


MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "TIFF"}


def detect_file(file_path: str, filename: str = "", declared_mime: str = "") -> dict:
    path = Path(file_path)
    if not path.is_file():
        raise ValueError("Input must be a regular file")
    size = path.stat().st_size
    if size > MAX_FILE_SIZE:
        raise ValueError("File exceeds 25 MiB limit")
    with path.open("rb") as stream:
        header = stream.read(512)
    mime, signature = "application/octet-stream", "unknown"
    for prefix, candidate, label in (
        (b"MZ", "application/x-dosexec", "PE/DOS executable"),
        (b"\x7fELF", "application/x-executable", "ELF executable"),
        (b"%PDF-", "application/pdf", "PDF"),
        (b"PK\x03\x04", "application/zip", "ZIP"),
        (b"PK\x05\x06", "application/zip", "ZIP"),
        (b"\x1f\x8b", "application/gzip", "GZIP"),
        (b"\xff\xd8\xff", "image/jpeg", "JPEG"),
        (b"\x89PNG\r\n\x1a\n", "image/png", "PNG"),
        (b"II*\x00", "image/tiff", "TIFF"),
        (b"MM\x00*", "image/tiff", "TIFF"),
        (b"7z\xbc\xaf\x27\x1c", "application/x-7z-compressed", "7Z"),
    ):
        if header.startswith(prefix):
            mime, signature = candidate, label
            break
    if header.startswith(b"RIFF") and header[8:12] == b"WEBP":
        mime, signature = "image/webp", "WEBP"
    if header[257:262] == b"ustar":
        mime, signature = "application/x-tar", "TAR"
    dimensions = None
    parser_validated = False
    if mime.startswith("image/"):
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if image.format not in IMAGE_FORMATS:
                    raise ValueError("Unsupported image format")
                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Image exceeds pixel limit")
                dimensions = [image.width, image.height]
                image.verify()
                parser_validated = True
    expected = mimetypes.guess_type(filename or path.name)[0]
    declared = declared_mime.split(";", 1)[0].strip().lower()
    findings = []
    if expected and expected != mime:
        findings.append("Filename extension does not match detected content")
    if declared and declared != mime:
        findings.append("Declared MIME does not match detected content")
    if mime in {"application/x-dosexec", "application/x-executable"}:
        findings.append("Executable content detected")
    if signature == "unknown":
        findings.append("Unsupported or unidentified content; processing denied")
    return {
        "size_bytes": size, "detected_mime": mime, "declared_mime": declared or None,
        "extension_mime": expected, "signature": signature, "magic_hex": header[:16].hex(),
        "parser_validated": parser_validated, "dimensions": dimensions, "warnings": findings,
    }