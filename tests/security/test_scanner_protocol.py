from unittest.mock import MagicMock, patch

import pytest

from fileshield.scanning import scan_file


@pytest.mark.parametrize("response,status", [(b"stream: OK\x00", "clean"),
                                             (b"stream: Test-Signature FOUND\x00", "infected"),
                                             (b"stream: size limit exceeded ERROR\x00", "unavailable")])
def test_scanner_response_is_not_overstated(tmp_path, response, status):
    path = tmp_path / "payload"
    path.write_bytes(b"synthetic test")
    version_socket = MagicMock()
    scan_socket = MagicMock()
    version_socket.__enter__.return_value = version_socket
    scan_socket.__enter__.return_value = scan_socket
    version_socket.recv.return_value = b"ClamAV test database\x00"
    scan_socket.recv.side_effect = [response, b""]
    with patch("fileshield.scanning.socket.create_connection", side_effect=[version_socket, scan_socket]):
        result = scan_file(str(path))
    assert result["status"] == status
    scan_socket.sendall.assert_any_call(b"zINSTREAM\x00")
    scan_socket.sendall.assert_any_call(b"\x00\x00\x00\x00")