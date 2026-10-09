import zipfile

import pytest
from pypdf import PdfWriter
from pypdf.actions import JavaScript

from fileshield.archives import analyze_archive, unsafe_entry
from fileshield.pdf import analyze_pdf, rewrite_pdf
from fileshield.protection import protect_file
from fileshield.scanning import scan_file


@pytest.mark.parametrize("name", ["../../etc/passwd", "/etc/passwd", "C:\\boot.ini", "..\\secret", "a\x00b", "file:stream"])
def test_path_traversal(name):
    assert unsafe_entry(name)


def test_archive_bomb(tmp_path):
    path = tmp_path / "bomb.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("payload", b"0" * 1_000_000)
    with pytest.raises(ValueError, match="expansion"):
        analyze_archive(str(path))


def test_archive_reports_traversal_and_nested(tmp_path):
    path = tmp_path / "hostile.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../../secret", b"secret")
        archive.writestr("nested.zip", b"PK")
    result = analyze_archive(str(path))
    assert "Unsafe entry path" in result["warnings"]
    assert result["extracted"] is False
    assert not (tmp_path.parent / "secret").exists()


def test_pdf_metadata_removal(tmp_path):
    original, output = tmp_path / "input.pdf", tmp_path / "clean.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_metadata({"/Author": "Private"})
    writer.write(original)
    rewrite_pdf([str(original)], str(output))
    assert analyze_pdf(str(output))["metadata"] == {}
    assert analyze_pdf(str(original))["metadata"]["/Author"] == "Private"


def test_pdf_script_refused(tmp_path):
    path = tmp_path / "script.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_open_action(JavaScript("app.alert('test')"))
    writer.write(path)
    assert "JavaScript" in analyze_pdf(str(path))["findings"]
    with pytest.raises(ValueError, match="manual review"):
        rewrite_pdf([str(path)], str(tmp_path / "clean.pdf"))


def test_encryption_round_trip_and_tampering(tmp_path):
    original, protected, restored = tmp_path / "file", tmp_path / "file.fs", tmp_path / "restored"
    original.write_bytes(b"private content")
    protect_file(str(original), str(protected), "correct horse battery staple")
    protect_file(str(protected), str(restored), "correct horse battery staple", decrypt=True)
    assert restored.read_bytes() == original.read_bytes()
    data = bytearray(protected.read_bytes())
    data[-1] ^= 1
    protected.write_bytes(data)
    with pytest.raises(ValueError, match="modified"):
        protect_file(str(protected), str(tmp_path / "bad"), "correct horse battery staple", decrypt=True)
    assert not (tmp_path / "bad").exists()


def test_unavailable_scanner_is_not_clean(tmp_path):
    path = tmp_path / "file"
    path.write_bytes(b"test")
    assert scan_file(str(path), host="127.0.0.1", port=1)["status"] == "unavailable"