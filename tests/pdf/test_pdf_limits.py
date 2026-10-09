import pytest
from pypdf import PdfWriter

from fileshield.pdf import MAX_PDF_PAGES, analyze_pdf


def test_pdf_page_limit(tmp_path):
    path = tmp_path / "pages.pdf"
    writer = PdfWriter()
    for index in range(MAX_PDF_PAGES + 1):
        writer.add_blank_page(width=10, height=10)
    writer.write(path)
    with pytest.raises(ValueError, match="page"):
        analyze_pdf(str(path))