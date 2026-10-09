"""ClamAV INSTREAM scanning with bounded I/O; unavailable means unavailable."""

import socket
import struct
from pathlib import Path

from fileshield.detection import MAX_FILE_SIZE


def scan_file(file_path: str, host: str = "clamav", port: int = 3310) -> dict:
    if Path(file_path).stat().st_size > MAX_FILE_SIZE:
        raise ValueError("Scanner input exceeds size limit")
    try:
        with socket.create_connection((host, port), timeout=10) as connection:
            connection.settimeout(20)
            connection.sendall(b"zVERSION\x00")
            version = connection.recv(1024).split(b"\x00", 1)[0].decode("utf-8", "replace")
        with socket.create_connection((host, port), timeout=10) as connection:
            connection.settimeout(20)
            connection.sendall(b"zINSTREAM\x00")
            with Path(file_path).open("rb") as stream:
                while chunk := stream.read(65536):
                    connection.sendall(struct.pack("!I", len(chunk)) + chunk)
            connection.sendall(struct.pack("!I", 0))
            response = bytearray()
            while len(response) < 4096:
                chunk = connection.recv(1024)
                if not chunk:
                    break
                response.extend(chunk)
                if b"\x00" in chunk:
                    break
            message = response.decode("utf-8", "replace").strip("\x00\r\n")
        if message.endswith(" FOUND"):
            return {"status": "infected", "scanner_version": version, "message": "Malware detected"}
        if message == "stream: OK":
            return {"status": "clean", "scanner_version": version,
                    "message": "No malware was detected by the configured scanner"}
    except OSError:
        pass
    return {"status": "unavailable", "scanner_version": None, "message": "Scan did not complete; processing denied"}