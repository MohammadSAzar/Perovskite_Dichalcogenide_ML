from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.document import (
    DocumentTextResult,
)
from psk_tmd.corpus.sections import (
    SectionedTextBlock,
    assign_pdf_block_sections,
)


# ---------------------------------------------------------------------------
# EVIDENCE CONTEXT WINDOW
# ---------------------------------------------------------------------------
class EvidenceContextWindow(BaseModel):
    page_number: int = Field(
        ge=1,
    )

    anchor_block_index: int = Field(
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    text: str

    block_indices: list[int] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# FIND SECTIONED BLOCK POSITION
# ---------------------------------------------------------------------------
def find_sectioned_block_position(
    blocks: list[SectionedTextBlock],
    page_number: int,
    block_index: int,
) -> int | None:
    for position, block in enumerate(
        blocks
    ):
        if (
            block.page_number
            == page_number
            and block.block_index
            == block_index
        ):
            return position

    return None


# ---------------------------------------------------------------------------
# SAME SCIENTIFIC SECTION
# ---------------------------------------------------------------------------
def is_same_scientific_section(
    anchor: SectionedTextBlock,
    candidate: SectionedTextBlock,
) -> bool:
    if (
        candidate.section_role
        != anchor.section_role
    ):
        return False

    if (
        anchor.section_title
        and candidate.section_title
        and candidate.section_title
        != anchor.section_title
    ):
        return False

    return True


# ---------------------------------------------------------------------------
# BUILD EVIDENCE CONTEXT WINDOW
# ---------------------------------------------------------------------------
def build_evidence_context_window(
    document: DocumentTextResult,
    page_number: int,
    block_index: int,
    previous_blocks: int = 0,
    next_blocks: int = 2,
) -> EvidenceContextWindow | None:
    if previous_blocks < 0:
        raise ValueError(
            "previous_blocks must be "
            "greater than or equal to zero."
        )

    if next_blocks < 0:
        raise ValueError(
            "next_blocks must be "
            "greater than or equal to zero."
        )

    sectioned_blocks = (
        assign_pdf_block_sections(
            document
        )
    )

    anchor_position = (
        find_sectioned_block_position(
            blocks=sectioned_blocks,
            page_number=page_number,
            block_index=block_index,
        )
    )

    if anchor_position is None:
        return None

    anchor = sectioned_blocks[
        anchor_position
    ]

    selected_blocks: list[
        SectionedTextBlock
    ] = [
        anchor,
    ]

    for offset in range(
        1,
        previous_blocks + 1,
    ):
        position = (
            anchor_position - offset
        )

        if position < 0:
            break

        candidate = sectioned_blocks[
            position
        ]

        if not is_same_scientific_section(
            anchor,
            candidate,
        ):
            break

        selected_blocks.insert(
            0,
            candidate,
        )

    for offset in range(
        1,
        next_blocks + 1,
    ):
        position = (
            anchor_position + offset
        )

        if position >= len(
            sectioned_blocks
        ):
            break

        candidate = sectioned_blocks[
            position
        ]

        if not is_same_scientific_section(
            anchor,
            candidate,
        ):
            break

        if (
            candidate.section_role
            == PaperSectionRole.REFERENCES
        ):
            break

        selected_blocks.append(
            candidate
        )

    text = normalize_whitespace(
        " ".join(
            block.text
            for block in selected_blocks
        )
    )

    return EvidenceContextWindow(
        page_number=anchor.page_number,
        anchor_block_index=(
            anchor.block_index
        ),
        section_title=(
            anchor.section_title
        ),
        section_role=(
            anchor.section_role
        ),
        text=text,
        block_indices=[
            block.block_index
            for block in selected_blocks
        ],
    )


