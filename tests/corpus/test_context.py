import pytest

from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.corpus.context import (
    build_evidence_context_window,
)
from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentTextResult,
)


# ---------------------------------------------------------------------------
# MAKE CONTEXT DOCUMENT
# ---------------------------------------------------------------------------
def make_context_document(
) -> DocumentTextResult:
    return DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=9,
                text="",
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text=(
                            "3.5. Possible "
                            "photocatalytic mechanism"
                        ),
                    ),
                    DocumentBlock(
                        block_index=2,
                        text=(
                            "Active-species trapping "
                            "experiments were performed "
                            "using several scavengers."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text=(
                            "The addition of BQ "
                            "strongly suppressed the "
                            "photocatalytic degradation."
                        ),
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "These results indicate "
                            "that superoxide radicals "
                            "are important active species."
                        ),
                    ),
                    DocumentBlock(
                        block_index=5,
                        text=(
                            "3.6. Photocatalytic "
                            "mechanism"
                        ),
                    ),
                    DocumentBlock(
                        block_index=6,
                        text=(
                            "The conduction-band and "
                            "valence-band positions "
                            "were then discussed."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text="",
        page_count=1,
        source_format="pdf",
        extraction_method=(
            "pymupdf_blocks"
        ),
    )


# ---------------------------------------------------------------------------
# COMPLETE EVIDENCE RESULT
# ---------------------------------------------------------------------------
def test_build_evidence_context_window():
    result = (
        build_evidence_context_window(
            document=(
                make_context_document()
            ),
            page_number=9,
            block_index=2,
            previous_blocks=0,
            next_blocks=2,
        )
    )

    assert result is not None

    assert (
        result.section_role
        == PaperSectionRole.MECHANISM
    )

    assert (
        result.block_indices
        == [
            2,
            3,
            4,
        ]
    )

    assert (
        "using several scavengers"
        in result.text
    )

    assert (
        "strongly suppressed"
        in result.text
    )

    assert (
        "superoxide radicals"
        in result.text
    )


# ---------------------------------------------------------------------------
# CONTEXT DOES NOT CROSS SECTION
# ---------------------------------------------------------------------------
def test_context_does_not_cross_section():
    result = (
        build_evidence_context_window(
            document=(
                make_context_document()
            ),
            page_number=9,
            block_index=4,
            previous_blocks=0,
            next_blocks=3,
        )
    )

    assert result is not None

    assert (
        "conduction-band"
        not in result.text
    )

    assert (
        result.block_indices
        == [
            4,
        ]
    )


# ---------------------------------------------------------------------------
# MISSING BLOCK RETURNS NONE
# ---------------------------------------------------------------------------
def test_missing_context_anchor_returns_none():
    result = (
        build_evidence_context_window(
            document=(
                make_context_document()
            ),
            page_number=9,
            block_index=99,
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# NEGATIVE WINDOW SIZE INVALID
# ---------------------------------------------------------------------------
def test_negative_context_window_invalid():
    with pytest.raises(
        ValueError,
    ):
        build_evidence_context_window(
            document=(
                make_context_document()
            ),
            page_number=9,
            block_index=2,
            next_blocks=-1,
        )


