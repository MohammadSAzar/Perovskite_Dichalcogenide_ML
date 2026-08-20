import fitz

import pytest

from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentTextResult,
)
from psk_tmd.corpus.pdf_text import extract_pdf_text


# ---------------------------------------------------------------------------
# DOCUMENT PAGE
# ---------------------------------------------------------------------------
def test_document_page_valid():
    page = DocumentPage(
        page_number=1,
        text="Test page.",
    )

    assert page.page_number == 1
    assert page.text == "Test page."


# ---------------------------------------------------------------------------
# DOCUMENT TEXT RESULT
# ---------------------------------------------------------------------------
def test_pdf_document_text_result_valid():
    result = DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=1,
                text="Page one.",
            ),
        ],
        sections=[],
        full_text="Page one.",
        page_count=1,
        source_format="pdf",
        extraction_method="pymupdf_blocks",
    )

    assert result.page_count == 1
    assert result.source_format == "pdf"
    assert result.extraction_method == "pymupdf_blocks"


# ---------------------------------------------------------------------------
# EXTRACT PDF TEXT
# ---------------------------------------------------------------------------
def test_extract_pdf_text(tmp_path):
    pdf_path = tmp_path / "test.pdf"

    document = fitz.open()

    page_1 = document.new_page()
    page_1.insert_text(
        (72, 72),
        "First page text.",
    )

    page_2 = document.new_page()
    page_2.insert_text(
        (72, 72),
        "Second page text.",
    )

    document.save(pdf_path)
    document.close()

    result = extract_pdf_text(pdf_path)

    assert result.page_count == 2
    assert result.source_format == "pdf"
    assert result.extraction_method == "pymupdf_blocks"

    assert len(result.pages) == 2
    assert result.sections == []

    assert result.pages[0].page_number == 1
    assert "First page text." in result.pages[0].text

    assert result.pages[1].page_number == 2
    assert "Second page text." in result.pages[1].text

    assert "First page text." in result.full_text
    assert "Second page text." in result.full_text

    assert len(result.pages[0].blocks) >= 1
    assert len(result.pages[1].blocks) >= 1

    assert (
            "First page text."
            in result.pages[0].blocks[0].text
    )

    assert (
            "Second page text."
            in result.pages[1].blocks[0].text
    )

    assert (
            result.extraction_method
            == "pymupdf_blocks"
    )


# ---------------------------------------------------------------------------
# MISSING PDF
# ---------------------------------------------------------------------------
def test_extract_pdf_text_rejects_missing_file(
    tmp_path,
):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_pdf_text(pdf_path)


# ---------------------------------------------------------------------------
# NON-PDF FILE
# ---------------------------------------------------------------------------
def test_extract_pdf_text_rejects_non_pdf(
    tmp_path,
):
    text_path = tmp_path / "test.txt"

    text_path.write_text(
        "Not a PDF.",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Expected a PDF file",
    ):
        extract_pdf_text(text_path)


