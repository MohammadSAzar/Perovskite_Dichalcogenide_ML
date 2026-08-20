import re

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


# ---------------------------------------------------------------------------
# SECTIONED TEXT BLOCK
# ---------------------------------------------------------------------------
class SectionedTextBlock(BaseModel):
    page_number: int = Field(
        ge=1,
    )

    block_index: int = Field(
        ge=1,
    )

    text: str

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )


# ---------------------------------------------------------------------------
# HEADING PREFIX
# ---------------------------------------------------------------------------
HEADING_PREFIX_PATTERN = re.compile(
    r"""
    ^
    (?:
        \d+
        (?:
            \.\d+
        )*
        [\.\)]?
        \s*
    )?
    """,
    flags=re.VERBOSE,
)


# ---------------------------------------------------------------------------
# SECTION HEADING PATTERNS
# ---------------------------------------------------------------------------
SECTION_HEADING_PATTERNS: tuple[
    tuple[
        re.Pattern[str],
        PaperSectionRole,
    ],
    ...,
] = (
    (
        re.compile(
            r"^references?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.REFERENCES,
    ),
    (
        re.compile(
            r"^bibliography$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.REFERENCES,
    ),
    (
        re.compile(
            r"^abstract$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.ABSTRACT,
    ),
    (
        re.compile(
            r"^introduction$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.INTRODUCTION,
    ),
    (
        re.compile(
            r"^background$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.INTRODUCTION,
    ),
    (
        re.compile(
            r"^(?:materials?\s+and\s+methods?|"
            r"methods?\s+and\s+materials?)$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^experimental(?:\s+section)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^experimental\s+methods?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^experimental\s+procedure$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^materials?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^(?:sample\s+)?preparation$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^synthesis(?:\s+procedure)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^characteri[sz]ation$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^photocatalytic\s+experiments?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^photocatalytic\s+activity"
            r"(?:\s+measurements?)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.EXPERIMENTAL,
    ),
    (
        re.compile(
            r"^results?(?:\s+and\s+discussion)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.RESULTS,
    ),
    (
        re.compile(
            r"^results?\s+and\s+discussions?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.RESULTS,
    ),
    (
        re.compile(
            r"^discussion$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.RESULTS,
    ),
    (
        re.compile(
            r"^(?:possible\s+|proposed\s+)?"
            r"photocatalytic\s+mechanism"
            r"(?:\s+analysis)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.MECHANISM,
    ),
    (
        re.compile(
            r"^(?:possible\s+|proposed\s+)?"
            r"charge(?:-|\s+)transfer\s+mechanism$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.MECHANISM,
    ),
    (
        re.compile(
            r"^(?:possible\s+|proposed\s+)?"
            r"electron(?:-|\s+)transfer\s+mechanism$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.MECHANISM,
    ),
    (
        re.compile(
            r"^mechanism(?:\s+analysis)?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.MECHANISM,
    ),
    (
        re.compile(
            r"^conclusions?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.CONCLUSION,
    ),
    (
        re.compile(
            r"^summary\s+and\s+conclusions?$",
            flags=re.IGNORECASE,
        ),
        PaperSectionRole.CONCLUSION,
    ),
)


# ---------------------------------------------------------------------------
# STRIP HEADING PREFIX
# ---------------------------------------------------------------------------
def strip_heading_prefix(
    text: str,
) -> str:
    clean_text = normalize_whitespace(
        text
    )

    return HEADING_PREFIX_PATTERN.sub(
        "",
        clean_text,
        count=1,
    ).strip()


# ---------------------------------------------------------------------------
# DETECT SECTION HEADING
# ---------------------------------------------------------------------------
def detect_section_heading(
    text: str,
) -> tuple[
    str,
    PaperSectionRole,
] | None:
    clean_text = normalize_whitespace(
        text
    )

    if not clean_text:
        return None

    if len(clean_text) > 120:
        return None

    heading_text = strip_heading_prefix(
        clean_text
    )

    heading_text = heading_text.rstrip(
        ":."
    ).strip()

    for pattern, section_role in (
        SECTION_HEADING_PATTERNS
    ):
        if pattern.fullmatch(
            heading_text
        ):
            return (
                clean_text,
                section_role,
            )

    return None


# ---------------------------------------------------------------------------
# ASSIGN PDF BLOCK SECTIONS
# ---------------------------------------------------------------------------
def assign_pdf_block_sections(
    document: DocumentTextResult,
) -> list[SectionedTextBlock]:
    sectioned_blocks: list[
        SectionedTextBlock
    ] = []

    current_title: str | None = None

    current_role = (
        PaperSectionRole.OTHER
    )

    for page in document.pages:
        if page.blocks:
            page_blocks = [
                (
                    block.block_index,
                    block.text,
                )
                for block in page.blocks
            ]
        else:
            page_blocks = [
                (
                    1,
                    page.text,
                )
            ]

        for block_index, block_text in (
            page_blocks
        ):
            if not normalize_whitespace(
                block_text
            ):
                continue

            heading = detect_section_heading(
                block_text
            )

            if heading is not None:
                current_title, current_role = (
                    heading
                )

            sectioned_blocks.append(
                SectionedTextBlock(
                    page_number=page.page_number,
                    block_index=block_index,
                    text=block_text,
                    section_title=current_title,
                    section_role=current_role,
                )
            )

    return sectioned_blocks


# ---------------------------------------------------------------------------
# CLASSIFY XML SECTION
# ---------------------------------------------------------------------------
def classify_xml_section(
    title: str | None,
) -> PaperSectionRole:
    if title is None:
        return PaperSectionRole.OTHER

    heading = detect_section_heading(
        title
    )

    if heading is None:
        return PaperSectionRole.OTHER

    _, section_role = heading

    return section_role

