import pytest
from PIL import Image

from fileshield.cli import main
from fileshield.hashing import compute_hashes


def test_metadata_and_sanitize_cli(tmp_path, capsys):
    source = tmp_path / "photo.png"
    Image.new("RGB", (8, 8)).save(source)
    main(["metadata", str(source)])
    assert '"privacy"' in capsys.readouterr().out
    main(["sanitize", str(source)])
    assert (tmp_path / "photo.cleaned.png").exists()


@pytest.mark.parametrize("size", [0, -1, False])
def test_invalid_hash_chunk_size(tmp_path, size):
    source = tmp_path / "file"
    source.write_bytes(b"data")
    with pytest.raises(ValueError):
        compute_hashes(str(source), chunk_size=size)


def test_variable_length_hash_rejected(tmp_path):
    source = tmp_path / "file"
    source.write_bytes(b"data")
    with pytest.raises(ValueError):
        compute_hashes(str(source), algorithms=("shake_128",))