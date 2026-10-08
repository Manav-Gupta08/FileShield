# Metadata and Privacy Findings

The Pillow extractor maps EXIF numeric tags to names and expands the EXIF and GPS sub-IFDs. Values may be bytes, rationals, tuples or dictionaries. Reports serialize unsupported JSON values as strings; this is presentation, not lossless metadata archival.

Image analysis also lists Pillow metadata container keys, such as `icc_profile`, `exif`, or textual fields. EXIF privacy findings group location data, identity/device details, and time/technical details instead of presenting only a raw tag dump.

The current classifier is heuristic and uses case-insensitive substring matching. Software is currently MEDIUM, not LOW. Orientation and image dimensions are LOW even though they are often necessary and may not identify a person. Empty EXIF scores zero, but zero does not imply complete privacy.

IPTC/XMP/ICC presence is not equivalent to full parsing. Comprehensive IPTC/XMP contents, every vendor MakerNote, embedded thumbnail reconstruction, media tags, and Office properties are not implemented. PDF properties are inspected separately. Do not report uninspected formats as metadata-free.