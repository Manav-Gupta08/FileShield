"""Versioned Scrypt + AES-GCM envelope, not a custom cipher."""

import os
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from fileshield.detection import MAX_FILE_SIZE


MAGIC = b"FSHIELD\x01"
OVERHEAD = len(MAGIC) + 16 + 12 + 16


def protect_file(file_path: str, output_path: str, password: str, decrypt: bool = False) -> dict:
    encoded = password.encode("utf-8")
    if len(encoded) < 12 or len(encoded) > 1024:
        raise ValueError("Password must contain 12-1024 UTF-8 bytes")
    path = Path(file_path)
    if path.stat().st_size > MAX_FILE_SIZE + (OVERHEAD if decrypt else 0):
        raise ValueError("Input exceeds encryption size limit")
    data = path.read_bytes()
    if decrypt:
        if not data.startswith(MAGIC) or len(data) < OVERHEAD:
            raise ValueError("Unsupported encrypted container")
        salt = data[len(MAGIC):len(MAGIC) + 16]
        nonce = data[len(MAGIC) + 16:len(MAGIC) + 28]
    else:
        salt, nonce = os.urandom(16), os.urandom(12)
    key = Scrypt(salt=salt, length=32, n=32768, r=8, p=1).derive(encoded)
    header = MAGIC + salt + nonce
    if decrypt:
        try:
            result = AESGCM(key).decrypt(nonce, data[len(header):], header)
        except InvalidTag as error:
            raise ValueError("Invalid password or modified container") from error
    else:
        result = header + AESGCM(key).encrypt(nonce, data, header)
    with Path(output_path).open("xb") as stream:
        stream.write(result)
    return {"operation": "decrypt" if decrypt else "encrypt", "cipher": "AES-256-GCM",
            "kdf": "Scrypt N=32768 r=8 p=1", "limitations": ["Python cannot guarantee password/key memory erasure"]}