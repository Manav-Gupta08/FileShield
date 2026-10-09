"""Inspect archives without extracting user-controlled paths."""

import gzip
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

from fileshield.detection import MAX_FILE_SIZE


MAX_ARCHIVE_FILES = 1000
MAX_EXTRACTED_SIZE = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".7z", ".rar", ".tgz"}
DANGEROUS_SUFFIXES = {".exe", ".dll", ".com", ".bat", ".cmd", ".ps1", ".sh", ".js", ".vbs", ".scr"}


def unsafe_entry(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return (not name or "\x00" in name or len(name) > 1024 or
            PurePosixPath(normalized).is_absolute() or bool(PureWindowsPath(name).drive) or
            ".." in PurePosixPath(normalized).parts or ":" in normalized)


def analyze_archive(file_path: str) -> dict:
    path = Path(file_path)
    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("Archive exceeds input size limit")
    with path.open("rb") as stream:
        signature = stream.read(2)
    entries, total, warnings = [], 0, []

    def record(name: str, size: int, compressed: int, special: bool = False):
        nonlocal total
        if len(entries) >= MAX_ARCHIVE_FILES:
            raise ValueError("Archive file count limit exceeded")
        total += size
        if total > MAX_EXTRACTED_SIZE or size / max(compressed, 1) > MAX_COMPRESSION_RATIO:
            raise ValueError("Archive expansion limit exceeded")
        suffix = PurePosixPath(name.replace("\\", "/")).suffix.lower()
        risks = []
        if unsafe_entry(name):
            risks.append("Unsafe entry path")
        if special:
            risks.append("Link, device, encrypted, or unsupported entry")
        if suffix in ARCHIVE_SUFFIXES:
            risks.append("Nested archive; recursive extraction is prohibited")
        if suffix in DANGEROUS_SUFFIXES:
            risks.append("Executable or script extension")
        entries.append({"name": name, "size": size, "compressed_size": compressed, "warnings": risks})
        warnings.extend(risks)

    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > MAX_ARCHIVE_FILES:
                raise ValueError("Archive file count limit exceeded")
            names = set()
            for member in members:
                if member.filename in names:
                    warnings.append("Duplicate archive entry")
                names.add(member.filename)
                mode = member.external_attr >> 16
                record(member.filename, member.file_size, member.compress_size,
                       stat.S_ISLNK(mode) or bool(member.flag_bits & 1))
    elif signature == b"\x1f\x8b":
        with gzip.open(path, "rb") as stream:
            while True:
                chunk = stream.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_EXTRACTED_SIZE or total / max(path.stat().st_size, 1) > MAX_COMPRESSION_RATIO:
                    raise ValueError("GZIP expansion limit exceeded")
        return {"entries": [], "uncompressed_size": total,
                "warnings": ["GZIP payload is not recursively interpreted"], "extracted": False}
    else:
        with tarfile.open(path, "r:") as archive:
            for member in archive:
                record(member.name, member.size, max(path.stat().st_size, 1),
                       not (member.isfile() or member.isdir()))
    return {"entries": entries, "uncompressed_size": total, "warnings": sorted(set(warnings)),
            "extracted": False, "limitations": ["Archive payloads are not malware-scanned individually",
                                                  "No extraction; maximum recursive processing depth is zero"]}