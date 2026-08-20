import re

from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.passages import (
    RelevantPassage,
)


# ---------------------------------------------------------------------------
# PAIR CANDIDATE
# ---------------------------------------------------------------------------
class PairCandidate(BaseModel):
    psk_formula_reported: str
    tmd_formula_reported: str

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    source_text: str

    score: float = Field(
        ge=0.0,
    )


# ---------------------------------------------------------------------------
# PAIR EXTRACTION RESULT
# ---------------------------------------------------------------------------
class PairExtractionResult(BaseModel):
    primary_pair_candidate: (
        PairCandidate | None
    ) = None

    pair_candidates: list[
        PairCandidate
    ] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# TMD METALS
# ---------------------------------------------------------------------------
TMD_METALS: tuple[str, ...] = (
    "Ti",
    "V",
    "Cr",
    "Mn",
    "Fe",
    "Co",
    "Ni",
    "Zr",
    "Nb",
    "Mo",
    "Tc",
    "Ru",
    "Rh",
    "Pd",
    "Hf",
    "Ta",
    "W",
    "Re",
    "Os",
    "Ir",
    "Pt",
)


# ---------------------------------------------------------------------------
# HETEROJUNCTION CONTEXT TERMS
# ---------------------------------------------------------------------------
HETEROJUNCTION_CONTEXT_TERMS: tuple[str, ...] = (
    "heterostructure",
    "heterojunction",
    "composite",
    "nanocomposite",
    "hybrid",
    "interface",
    "coupled",
    "coupling",
)


# ---------------------------------------------------------------------------
# PRIMARY-STUDY TERMS
# ---------------------------------------------------------------------------
PRIMARY_STUDY_TERMS: tuple[str, ...] = (
    "in this study",
    "in this work",
    "in this paper",
    "we prepared",
    "we synthesized",
    "we fabricated",
    "was prepared",
    "were prepared",
    "was synthesized",
    "were synthesized",
    "was fabricated",
    "were fabricated",
    "was constructed",
    "were constructed",
)


# ---------------------------------------------------------------------------
# SECTION PRIORITY
# ---------------------------------------------------------------------------
SECTION_PRIORITY: dict[
    PaperSectionRole,
    float,
] = {
    PaperSectionRole.ABSTRACT: 4.0,
    PaperSectionRole.MECHANISM: 3.5,
    PaperSectionRole.RESULTS: 3.0,
    PaperSectionRole.CONCLUSION: 3.0,
    PaperSectionRole.OTHER: 2.0,
    PaperSectionRole.EXPERIMENTAL: 1.5,
    PaperSectionRole.INTRODUCTION: 0.5,
    PaperSectionRole.REFERENCES: 0.0,
}


# ---------------------------------------------------------------------------
# PSK FORMULA PATTERN
# ---------------------------------------------------------------------------
PSK_FORMULA_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?:"
    r"[A-Z][a-z]?"
    r"(?:\d+(?:\.\d+)?)?"
    r"){2,5}"
    r"O"
    r"(?:"
    r"3(?:\.\d+)?"
    r"(?:[-−–]?[δx])?"
    r")"
    r"(?![A-Za-z0-9])"
)


# ---------------------------------------------------------------------------
# TMD METAL PATTERN
# ---------------------------------------------------------------------------
TMD_METAL_PATTERN = (
    r"(?:"
    + "|".join(
        sorted(
            TMD_METALS,
            key=len,
            reverse=True,
        )
    )
    + r")"
)


# ---------------------------------------------------------------------------
# TMD FORMULA PATTERN
# ---------------------------------------------------------------------------
TMD_FORMULA_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(?:"
    + TMD_METAL_PATTERN
    + r"(?:\d+(?:\.\d+)?)?"
    r"){1,3}"
    r"(?:"
    r"(?:S|Se|Te)2"
    r"|"
    r"(?:S|Se|Te)"
    r"\d+(?:\.\d+)?"
    r"(?:S|Se|Te)"
    r"\d+(?:\.\d+)?"
    r")"
    r"(?![A-Za-z0-9])"
)


# ---------------------------------------------------------------------------
# DEDUPLICATE FORMULAS
# ---------------------------------------------------------------------------
def deduplicate_formulas(
    formulas: list[str],
) -> list[str]:
    unique: list[str] = []

    seen: set[str] = set()

    for formula in formulas:
        if formula in seen:
            continue

        seen.add(
            formula
        )

        unique.append(
            formula
        )

    return unique


# ---------------------------------------------------------------------------
# EXTRACT PSK FORMULAS
# ---------------------------------------------------------------------------
def extract_psk_formulas(
    text: str,
) -> list[str]:
    clean_text = normalize_whitespace(
        text
    )

    formulas = [
        match.group(0)
        for match
        in PSK_FORMULA_PATTERN.finditer(
            clean_text
        )
    ]

    return deduplicate_formulas(
        formulas
    )


# ---------------------------------------------------------------------------
# EXTRACT TMD FORMULAS
# ---------------------------------------------------------------------------
def extract_tmd_formulas(
    text: str,
) -> list[str]:
    clean_text = normalize_whitespace(
        text
    )

    formulas = [
        match.group(0)
        for match
        in TMD_FORMULA_PATTERN.finditer(
            clean_text
        )
    ]

    return deduplicate_formulas(
        formulas
    )


# ---------------------------------------------------------------------------
# CHECK HETEROJUNCTION CONTEXT
# ---------------------------------------------------------------------------
def has_heterojunction_context(
    text: str,
) -> bool:
    lower_text = text.lower()

    return any(
        term in lower_text
        for term
        in HETEROJUNCTION_CONTEXT_TERMS
    )


# ---------------------------------------------------------------------------
# CHECK PRIMARY-STUDY CONTEXT
# ---------------------------------------------------------------------------
def has_primary_study_context(
    text: str,
) -> bool:
    lower_text = text.lower()

    return any(
        term in lower_text
        for term
        in PRIMARY_STUDY_TERMS
    )


# ---------------------------------------------------------------------------
# CHECK EXPLICIT PAIR LINK
# ---------------------------------------------------------------------------
def is_explicit_pair_link(
    between_text: str,
) -> bool:
    return (
        re.fullmatch(
            r"\s*"
            r"(?:\([^)]{0,50}\)\s*)?"
            r"/"
            r"\s*"
            r"(?:\([^)]{0,50}\)\s*)?",
            between_text,
        )
        is not None
    )


# ---------------------------------------------------------------------------
# SCORE PAIR CANDIDATE
# ---------------------------------------------------------------------------
def score_pair_candidate(
    text: str,
    section_role: PaperSectionRole,
) -> float:
    score = 5.0

    score += SECTION_PRIORITY.get(
        section_role,
        0.0,
    )

    if has_heterojunction_context(
        text
    ):
        score += 2.0

    if has_primary_study_context(
        text
    ):
        score += 2.0

    lower_text = text.lower()

    if (
        "mechanism" in lower_text
        or "charge transfer" in lower_text
        or "charge-transfer" in lower_text
    ):
        score += 1.0

    return score


# ---------------------------------------------------------------------------
# EXTRACT RAW PAIR CANDIDATES
# ---------------------------------------------------------------------------
def extract_raw_pair_candidates(
    passages: list[RelevantPassage],
) -> list[PairCandidate]:
    candidates: list[
        PairCandidate
    ] = []

    for passage in passages:
        clean_text = normalize_whitespace(
            passage.text
        )

        psk_matches = list(
            PSK_FORMULA_PATTERN.finditer(
                clean_text
            )
        )

        tmd_matches = list(
            TMD_FORMULA_PATTERN.finditer(
                clean_text
            )
        )

        for psk_match in psk_matches:
            for tmd_match in tmd_matches:
                if (
                    psk_match.end()
                    <= tmd_match.start()
                ):
                    between_text = clean_text[
                        psk_match.end():
                        tmd_match.start()
                    ]

                elif (
                    tmd_match.end()
                    <= psk_match.start()
                ):
                    between_text = clean_text[
                        tmd_match.end():
                        psk_match.start()
                    ]

                else:
                    continue

                if not is_explicit_pair_link(
                    between_text
                ):
                    continue

                candidates.append(
                    PairCandidate(
                        psk_formula_reported=(
                            psk_match.group(0)
                        ),
                        tmd_formula_reported=(
                            tmd_match.group(0)
                        ),
                        page_number=(
                            passage.page_number
                        ),
                        section_title=(
                            passage.section_title
                        ),
                        section_role=(
                            passage.section_role
                        ),
                        source_text=(
                            passage.text
                        ),
                        score=(
                            score_pair_candidate(
                                text=passage.text,
                                section_role=(
                                    passage.section_role
                                ),
                            )
                        ),
                    )
                )

    return candidates


# ---------------------------------------------------------------------------
# CONSOLIDATE PAIR CANDIDATES
# ---------------------------------------------------------------------------
def consolidate_pair_candidates(
    candidates: list[
        PairCandidate
    ],
) -> list[PairCandidate]:
    best_by_pair: dict[
        tuple[
            str,
            str,
        ],
        PairCandidate,
    ] = {}

    for candidate in candidates:
        key = (
            candidate.psk_formula_reported,
            candidate.tmd_formula_reported,
        )

        current = best_by_pair.get(
            key
        )

        if (
            current is None
            or candidate.score
            > current.score
        ):
            best_by_pair[
                key
            ] = candidate

    return sorted(
        best_by_pair.values(),
        key=lambda candidate: (
            -candidate.score,
            candidate.page_number
            if candidate.page_number
            is not None
            else 9999,
            candidate.psk_formula_reported,
            candidate.tmd_formula_reported,
        ),
    )


# ---------------------------------------------------------------------------
# SELECT PRIMARY PAIR CANDIDATE
# ---------------------------------------------------------------------------
def select_primary_pair_candidate(
    candidates: list[
        PairCandidate
    ],
) -> PairCandidate | None:
    if not candidates:
        return None

    return candidates[0]


# ---------------------------------------------------------------------------
# EXTRACT PAIR CANDIDATES
# ---------------------------------------------------------------------------
def extract_pair_candidates(
    passages: list[RelevantPassage],
) -> PairExtractionResult:
    raw_pair_candidates = (
        extract_raw_pair_candidates(
            passages
        )
    )

    pair_candidates = (
        consolidate_pair_candidates(
            raw_pair_candidates
        )
    )

    primary_pair_candidate = (
        select_primary_pair_candidate(
            pair_candidates
        )
    )

    return PairExtractionResult(
        primary_pair_candidate=(
            primary_pair_candidate
        ),
        pair_candidates=(
            pair_candidates
        ),
    )

