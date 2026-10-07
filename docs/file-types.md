# File Identification

`fileshield/detection.py` reads at most 512 header bytes after checking a 25 MiB input bound. It recognizes selected image, PDF, executable and archive signatures. Pillow verifies recognized JPEG/PNG/WebP/TIFF structure and checks a 20-million-pixel ceiling.

Filename MIME uses `mimetypes` only as a comparison signal. Declared MIME is independently compared with content evidence. A mismatch is reported during analysis and blocks image/sanitization processing. Executables can be analyzed as evidence; they are never executed.

`parser_validated=false` means only a signature has been identified at this layer. A valid signature does not prove the entire file is valid or safe. Unknown data remains `application/octet-stream`; its filename never upgrades trust. Generic hashing and encryption can operate on arbitrary bytes.

This is a bounded signature table, not libmagic integration. Polyglots, legacy Office/OLE, detailed OOXML recognition, executable architecture validation, and complete format coverage remain release-roadmap work. Platform `mimetypes` databases can differ; conservative mismatch rejection can reject legitimate aliases.

Regression evidence: `tests/unit/test_detection.py` checks disguised executables, verified PNG dimensions, truncated PNGs, and unidentified content.