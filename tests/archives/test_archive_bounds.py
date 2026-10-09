import gzip
import zipfile

import pytest

from fileshield.archives import MAX_ARCHIVE_FILES, analyze_archive


def test_too_many_entries_are_refused(tmp_path):
    path = tmp_path / "entries.zip"
    with zipfile.ZipFile(path, "w") as archive:
        for index in range(MAX_ARCHIVE_FILES + 1):
            archive.writestr(str(index), b"x")
    with pytest.raises(ValueError, match="count"):
        analyze_archive(str(path))


def test_gzip_expansion_is_bounded(tmp_path):
    path = tmp_path / "payload.gz"
    with gzip.open(path, "wb") as stream:
        stream.write(b"0" * 1_000_000)
    with pytest.raises(ValueError, match="expansion"):
        analyze_archive(str(path))