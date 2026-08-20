import re

from enum import Enum

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
    assign_pdf_block_sections,
    classify_xml_section,
)


# ---------------------------------------------------------------------------
# PASSAGE CATEGORY
# ---------------------------------------------------------------------------
class PassageCategory(str, Enum):
    MECHANISM = "mechanism"
    MATERIAL = "material"
    PHOTOCATALYTIC_TEST = (
        "photocatalytic_test"
    )
    SYNTHESIS = "synthesis"


# ---------------------------------------------------------------------------
# RELEVANT PASSAGE
# ---------------------------------------------------------------------------
class RelevantPassage(BaseModel):
    passage_id: str

    category: PassageCategory

    text: str

    matched_terms: list[str] = Field(
        default_factory=list,
    )

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )


# ---------------------------------------------------------------------------
# KEYWORD GROUPS
# ---------------------------------------------------------------------------
PASSAGE_KEYWORDS: dict[
    PassageCategory,
    tuple[str, ...],
] = {
    PassageCategory.MECHANISM: (
        "mechanism",
        "charge transfer",
        "charge-transfer",
        "electron transfer",
        "hole transfer",
        "carrier transfer",
        "carrier migration",
        "band alignment",
        "band position",
        "conduction band",
        "valence band",
        "mott-schottky",
        "mott schottky",
        "z-scheme",
        "z scheme",
        "s-scheme",
        "s scheme",
        "type-i",
        "type i",
        "type-ii",
        "type ii",
        "type-iii",
        "type iii",
        "straddling",
        "staggered",
        "broken-gap",
        "broken gap",
        "schottky",
        "p-n junction",
        "pn junction",
        "built-in electric field",
        "internal electric field",
        "work function",
        "xps",
        "photocurrent",
        "impedance",
        "eis",
        "photoluminescence",
        "radical",
        "scavenger",
        "quenching",
        "active species",
        "esr",
        "spin trapping",
        "surface photovoltage",
        "kelvin probe",
        "photodeposition",
    ),
    PassageCategory.MATERIAL: (
        "heterostructure",
        "heterojunction",
        "composite",
        "nanocomposite",
        "wt%",
        "wt %",
        "mass ratio",
        "weight ratio",
        "molar ratio",
        "doped",
        "dopant",
        "substitution",
        "phase",
        "space group",
        "xrd",
        "hrtem",
        "tem",
        "sem",
        "interface",
        "lattice spacing",
    ),
    PassageCategory.PHOTOCATALYTIC_TEST: (
        "photocatalytic",
        "photocatalysis",
        "hydrogen evolution",
        "hydrogen production",
        "h2 evolution",
        "degradation",
        "removal efficiency",
        "degradation efficiency",
        "xenon lamp",
        "xe lamp",
        "visible light",
        "cutoff filter",
        "cut-off filter",
        "sacrificial agent",
        "cocatalyst",
        "dark adsorption",
        "dark equilibration",
        "adsorption-desorption equilibrium",
        "quantum yield",
        "aqy",
        "apparent quantum",
        "cycle",
        "recycling",
        "stability",
    ),
    PassageCategory.SYNTHESIS: (
        "synthesized",
        "synthesis",
        "prepared",
        "preparation",
        "hydrothermal",
        "solvothermal",
        "sol-gel",
        "calcined",
        "calcination",
        "one-pot",
        "one pot",
        "in-situ",
        "in situ",
        "ultrasonication",
        "sonicated",
        "precursor",
    ),
}


# ---------------------------------------------------------------------------
# AMBIGUOUS TYPE KEYWORDS
# ---------------------------------------------------------------------------
AMBIGUOUS_TYPE_KEYWORDS: set[str] = {
    "type-i",
    "type i",
    "type-ii",
    "type ii",
    "type-iii",
    "type iii",
}


# ---------------------------------------------------------------------------
# BET CONTEXT TERMS
# ---------------------------------------------------------------------------
BET_CONTEXT_TERMS: tuple[str, ...] = (
    "bet",
    "brunauer-emmett-teller",
    "brunauer–emmett–teller",
    "adsorption isotherm",
    "adsorption isotherms",
    "desorption isotherm",
    "desorption isotherms",
    "adsorption-desorption",
    "adsorption–desorption",
    "nitrogen adsorption",
    "n2 adsorption",
    "n₂ adsorption",
    "specific surface area",
    "surface area",
    "pore volume",
    "pore size",
    "hysteresis loop",
)


# ---------------------------------------------------------------------------
# SPLIT TEXT INTO PARAGRAPHS
# ---------------------------------------------------------------------------
def split_into_paragraphs(
    text: str,
) -> list[str]:
    paragraphs: list[str] = []

    for block in text.split("\n"):
        clean_block = normalize_whitespace(
            block
        )

        if clean_block:
            paragraphs.append(
                clean_block
            )

    return paragraphs


# ---------------------------------------------------------------------------
# KEYWORD PATTERN
# ---------------------------------------------------------------------------
def build_keyword_pattern(
    keyword: str,
) -> re.Pattern[str]:
    escaped = re.escape(
        keyword
    )

    return re.compile(
        rf"(?<![A-Za-z0-9])"
        rf"{escaped}"
        rf"(?![A-Za-z0-9])",
        flags=re.IGNORECASE,
    )


# ---------------------------------------------------------------------------
# CHECK BET CONTEXT
# ---------------------------------------------------------------------------
def is_bet_context(
    text: str,
) -> bool:
    lower_text = text.lower()

    return any(
        term.lower() in lower_text
        for term in BET_CONTEXT_TERMS
    )


# ---------------------------------------------------------------------------
# FIND MATCHED TERMS
# ---------------------------------------------------------------------------
def find_matched_terms(
    text: str,
    keywords: tuple[str, ...],
) -> list[str]:
    matched_terms: list[str] = []

    bet_context = is_bet_context(
        text
    )

    for keyword in keywords:
        pattern = build_keyword_pattern(
            keyword
        )

        if not pattern.search(
            text
        ):
            continue

        if (
            keyword == "schottky"
            and re.search(
                r"mott[-\s]schottky",
                text,
                flags=re.IGNORECASE,
            )
        ):
            continue

        if (
            keyword
            in AMBIGUOUS_TYPE_KEYWORDS
            and bet_context
        ):
            continue

        matched_terms.append(
            keyword
        )

    return matched_terms


# ---------------------------------------------------------------------------
# SELECT PASSAGES FROM PDF PAGES
# ---------------------------------------------------------------------------
def select_page_passages(
    document: DocumentTextResult,
) -> list[RelevantPassage]:
    passages: list[
        RelevantPassage
    ] = []

    passage_number = 1

    sectioned_blocks = (
        assign_pdf_block_sections(
            document
        )
    )

    for block in sectioned_blocks:
        if (
            block.section_role
            == PaperSectionRole.REFERENCES
        ):
            continue

        paragraphs = split_into_paragraphs(
            block.text
        )

        for paragraph in paragraphs:
            for category, keywords in (
                PASSAGE_KEYWORDS.items()
            ):
                matched_terms = (
                    find_matched_terms(
                        paragraph,
                        keywords,
                    )
                )

                if not matched_terms:
                    continue

                passages.append(
                    RelevantPassage(
                        passage_id=(
                            f"PAS-"
                            f"{passage_number:04d}"
                        ),
                        category=category,
                        text=paragraph,
                        matched_terms=matched_terms,
                        page_number=(
                            block.page_number
                        ),
                        section_title=(
                            block.section_title
                        ),
                        section_role=(
                            block.section_role
                        ),
                    )
                )

                passage_number += 1

    return passages


# ---------------------------------------------------------------------------
# SELECT PASSAGES FROM XML SECTIONS
# ---------------------------------------------------------------------------
def select_section_passages(
    document: DocumentTextResult,
) -> list[RelevantPassage]:
    passages: list[
        RelevantPassage
    ] = []

    passage_number = 1

    for section in document.sections:
        section_role = (
            classify_xml_section(
                section.title
            )
        )

        if (
            section_role
            == PaperSectionRole.REFERENCES
        ):
            continue

        paragraphs = split_into_paragraphs(
            section.text
        )

        for paragraph in paragraphs:
            search_text = paragraph

            if section.title:
                search_text = (
                    f"{section.title} "
                    f"{paragraph}"
                )

            for category, keywords in (
                PASSAGE_KEYWORDS.items()
            ):
                matched_terms = (
                    find_matched_terms(
                        search_text,
                        keywords,
                    )
                )

                if not matched_terms:
                    continue

                passages.append(
                    RelevantPassage(
                        passage_id=(
                            f"PAS-"
                            f"{passage_number:04d}"
                        ),
                        category=category,
                        text=paragraph,
                        matched_terms=matched_terms,
                        page_number=None,
                        section_title=(
                            section.title
                        ),
                        section_role=(
                            section_role
                        ),
                    )
                )

                passage_number += 1

    return passages


# ---------------------------------------------------------------------------
# SELECT RELEVANT PASSAGES
# ---------------------------------------------------------------------------
def select_relevant_passages(
    document: DocumentTextResult,
) -> list[RelevantPassage]:
    if document.source_format == "pdf":
        return select_page_passages(
            document
        )

    if document.source_format == "xml":
        return select_section_passages(
            document
        )

    raise ValueError(
        "Unsupported document source format: "
        f"{document.source_format}"
    )

