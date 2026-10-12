"""Generated paths only; user filenames are display labels, not paths."""

import re
import shutil
import uuid
from pathlib import Path

from backend.config import settings


def job_directory(identifier: str) -> Path:
    normalized = str(uuid.UUID(identifier))
    if identifier != normalized:
        raise ValueError("Canonical UUID required")
    return settings.storage.resolve() / normalized


def display_filename(name: str) -> str:
    if not name or "\x00" in name or len(name) > 255:
        raise ValueError("Invalid filename")
    normalized = name.replace("\\", "/").split("/")[-1]
    cleaned = re.sub(r"[^a-zA-Z0-9_. -]", "_", normalized).strip(" .")
    if not cleaned:
        raise ValueError("Invalid filename")
    return cleaned


def remove_job_files(identifier: str):
    directory = job_directory(identifier)
    if directory.exists():
        shutil.rmtree(directory)