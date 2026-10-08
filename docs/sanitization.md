# Sanitized Copies

Image sanitization follows `validate -> decode -> apply EXIF orientation -> copy pixels into a new image -> encode -> inspect output`. Rebuilding a new image avoids copying Pillow's source metadata dictionary, EXIF, embedded thumbnail, ICC, and text chunks into the destination.

An explicit before/after record lists removed and remaining EXIF fields, metadata container keys, and limitations. The original is never overwritten, and output paths use exclusive `xb` creation. The API uses generated names; the CLI defaults to `.cleaned.png`.

Resize uses aspect-preserving thumbnail semantics: width/height are maxima, not forced exact dimensions, and it never enlarges. Crop is validated against the oriented image. Rotation is restricted to quarter turns. Quality applies to JPEG/WebP, not lossless PNG/TIFF. DPI is optional and is not encoded for WebP.

Images with multiple frames are rejected, rather than silently losing animation or pages. Dropping ICC can alter color appearance; RGBA-to-JPEG conversion discards alpha. Visible faces, text, location clues, steganographic content, encoder signatures and format-required fields remain outside the privacy guarantee.

PDF rewriting is intentionally conservative; see `pdf.md`. No Office sanitizer is presently exposed. Sanitization is not antivirus, redaction, content disarm, or forensic erasure.