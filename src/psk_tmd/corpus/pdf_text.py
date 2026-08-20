from pathlib import Path

import pymupdf

from psk_tmd.common.text_utils import normalize_whitespace
from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentTextResult,
)


# ---------------------------------------------------------------------------
# EXTRACT PDF TEXT
# ---------------------------------------------------------------------------
def extract_pdf_text(
    path: str | Path,
) -> DocumentTextResult:
    pdf_path = Path(path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file does not exist: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            f"PDF path is not a file: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Expected a PDF file, got: {pdf_path.name}"
        )

    pages: list[DocumentPage] = []

    try:
        with pymupdf.open(pdf_path) as document:
            if not document.is_pdf:
                raise ValueError(
                    f"File is not a valid PDF: {pdf_path}"
                )

            for page_index, page in enumerate(
                document,
                start=1,
            ):
                raw_blocks = page.get_text(
                    "blocks"
                )

                blocks: list[DocumentBlock] = []

                for block_index, block in enumerate(
                    raw_blocks,
                    start=1,
                ):
                    raw_text = block[4]

                    clean_text = normalize_whitespace(
                        raw_text
                    )

                    if not clean_text:
                        continue

                    blocks.append(
                        DocumentBlock(
                            block_index=block_index,
                            text=clean_text,
                        )
                    )

                page_text = "\n".join(
                    block.text
                    for block in blocks
                )

                pages.append(
                    DocumentPage(
                        page_number=page_index,
                        text=page_text,
                        blocks=blocks,
                    )
                )

    except (
        pymupdf.FileDataError,
        RuntimeError,
    ) as exc:
        raise ValueError(
            f"Could not read PDF file: {pdf_path}"
        ) from exc

    full_text = "\n\n".join(
        page.text
        for page in pages
        if page.text
    )

    return DocumentTextResult(
        pages=pages,
        sections=[],
        full_text=full_text,
        page_count=len(pages),
        source_format="pdf",
        extraction_method="pymupdf_blocks",
    )


