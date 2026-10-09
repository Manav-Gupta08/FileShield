# Password Protection and Encryption

Generic protection uses the established `cryptography` package. Each envelope has a version magic, 16-byte random salt, 12-byte random nonce, and AES-GCM ciphertext/tag. Scrypt derives a 32-byte key with `N=32768, r=8, p=1`. The version/salt/nonce header is authenticated as associated data.

Passwords must contain 12-1,024 UTF-8 bytes in the engine; API schema is additionally capped at 256 characters. Files are bounded to 25 MiB; decryption accepts envelope overhead at the engine level. The web upload limit remains 25 MiB, so a protected file produced from a near-limit original may need the CLI for decryption.

Wrong passwords and modified ciphertext return one generic failure and create no plaintext output. CLI passwords are prompted with `getpass`. API passwords are transmitted only over the configured connection and encrypted at rest in job options using a separate server key; they are not put in Celery messages, which carry only job UUIDs. Options are cleared after normal completion/failure or timeout.

Authentication passwords use Argon2id, not Scrypt encryption keys or SHA file digests. Session bearer material is stored as SHA-256 of a random high-entropy token, not as plaintext. Password hashing verifies a guess; key derivation produces encryption material; encryption is reversible with the key; file hashing is a digest.

Python cannot promise zeroization of password/key memory. Lost passwords cannot be recovered. This custom envelope framing is not compatible with ordinary password-protected ZIP tools. No password cracking, external vault integration, streaming very-large-file encryption, or automatic key rotation is implemented. Obtain cryptographic design review and tune KDF costs on deployment hardware before release.