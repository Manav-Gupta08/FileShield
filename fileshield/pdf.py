"""Bounded PDF inspection and conservative rewrites using pypdf."""

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, IndirectObject

from fileshield.detection import detect_file


MAX_PDF_PAGES = 200
MAX_PDF_OBJECTS = 10000
RISK_KEYS = {"/JS": "JavaScript", "/JavaScript": "JavaScript", "/EmbeddedFiles": "Embedded files",
             "/EF": "Embedded files", "/AcroForm": "Forms", "/URI": "External URLs",
             "/Launch": "Launch action", "/AA": "Automatic actions", "/OpenAction": "Open action",
             "/Annots": "Annotations", "/Sig": "Digital signature", "/RichMedia": "Rich media",
             "/XFA": "XFA forms"}


def open_pdf(file_path: str, password: str | None = None) -> PdfReader:
    if detect_file(file_path)["detected_mime"] != "application/pdf":
        raise ValueError("PDF signature required")
    reader = PdfReader(file_path, strict=True)
    if reader.is_encrypted and (not password or not reader.decrypt(password)):
        raise ValueError("An existing valid PDF password is required")
    if len(reader.pages) > MAX_PDF_PAGES:
        raise ValueError("PDF page limit exceeded")
    return reader


def analyze_pdf(file_path: str, password: str | None = None) -> dict:
    reader = open_pdf(file_path, password)
    found, visited = set(), set()
    pending = [reader.trailer]
    count = 0
    while pending:
        item = pending.pop()
        count += 1
        if count > MAX_PDF_OBJECTS:
            raise ValueError("PDF object traversal limit exceeded")
        if isinstance(item, IndirectObject):
            reference = (item.idnum, item.generation)
            if reference in visited:
                continue
            visited.add(reference)
            item = item.get_object()
        if isinstance(item, DictionaryObject):
            for key, value in item.items():
                if str(key) in RISK_KEYS:
                    found.add(RISK_KEYS[str(key)])
                if str(value) == "/Sig":
                    found.add("Digital signature")
                pending.append(value)
        elif isinstance(item, ArrayObject):
            pending.extend(item)
    return {"pages": len(reader.pages), "encrypted": reader.is_encrypted,
            "metadata": {str(key): str(value) for key, value in (reader.metadata or {}).items()},
            "xmp_present": "/Metadata" in reader.trailer["/Root"], "findings": sorted(found),
            "limitations": ["Heuristic reachable-object inspection, not a malware verdict",
                            "Signed documents lose signature validity when rewritten"]}


def rewrite_pdf(file_paths: list[str], output_path: str, pages: list[int] | None = None,
                rotation: int = 0, password: str | None = None) -> dict:
    if not file_paths or len(file_paths) > 10 or rotation not in {0, 90, 180, 270}:
        raise ValueError("Invalid PDF operation")
    writer = PdfWriter()
    reports = []
    for file_path in file_paths:
        report = analyze_pdf(file_path, password)
        if report["findings"]:
            raise ValueError("Active, embedded, annotated, form, or signed PDFs require manual review")
        reader = open_pdf(file_path, password)
        chosen = pages if pages is not None else list(range(len(reader.pages)))
        if not chosen or any(index < 0 or index >= len(reader.pages) for index in chosen):
            raise ValueError("Page indices must be valid zero-based indices")
        if len(writer.pages) + len(chosen) > MAX_PDF_PAGES:
            raise ValueError("Output PDF page limit exceeded")
        for index in chosen:
            page = reader.pages[index]
            page.pop("/Metadata", None)
            if rotation:
                page.rotate(rotation)
            writer.add_page(page)
        reports.append(report)
    writer.metadata = None
    output = Path(output_path)
    with output.open("xb") as stream:
        try:
            writer.write(stream)
        except BaseException:
            stream.close()
            output.unlink(missing_ok=True)
            raise
    try:
        after = analyze_pdf(str(output))
        if after["findings"] or after["metadata"] or after["xmp_present"]:
            raise ValueError("Output failed PDF metadata/security validation")
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"before": reports, "after": after,
            "limitations": ["Visible text, image metadata and revision evidence may remain",
                            "Not a PDF content-disarm guarantee"]}