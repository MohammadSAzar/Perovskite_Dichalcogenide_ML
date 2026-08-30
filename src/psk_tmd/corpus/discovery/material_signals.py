import re

from dataclasses import (
    dataclass,
)


# ---------------------------------------------------------------------------
# MATERIAL SIGNAL RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MaterialSignalResult:
    has_perovskite_signal: bool

    has_tmd_signal: bool

    matched_perovskite_terms: tuple[str, ...]

    matched_perovskite_formulas: tuple[str, ...]

    matched_tmd_terms: tuple[str, ...]


# ---------------------------------------------------------------------------
# MATERIAL TERMS
# ---------------------------------------------------------------------------
PEROVSKITE_TERMS = (
    "perovskite",
    "perovskites",
    "perovskite-type",
    "perovskite type",
    "perovskite-like",
    "perovskite like",
)

TMD_TERMS = (
    "mos2",
    "ws2",
    "mose2",
    "wse2",
    "mote2",
    "wte2",
    "mosse",
    "wsse",
    "transition metal dichalcogenide",
    "transition-metal dichalcogenide",
    "transition metal dichalcogenides",
    "transition-metal dichalcogenides",
)


# ---------------------------------------------------------------------------
# OXIDE PEROVSKITE FORMULA PATTERN
# ---------------------------------------------------------------------------
OXIDE_PEROVSKITE_FORMULA_PATTERN = re.compile(
    r"\b"
    r"(?:[A-Z][a-z]?"
    r"(?:\d+(?:\.\d+)?)?)"
    r"{2}"
    r"O3"
    r"\b"
)


# ---------------------------------------------------------------------------
# NORMALIZE MATERIAL TEXT
# ---------------------------------------------------------------------------
def normalize_material_text(
    value: str,
) -> str:
    return (
        value
        .replace(
            "₂",
            "2",
        )
        .replace(
            "₃",
            "3",
        )
        .replace(
            "–",
            "-",
        )
        .replace(
            "—",
            "-",
        )
    )


# ---------------------------------------------------------------------------
# FIND TERM MATCHES
# ---------------------------------------------------------------------------
def find_material_terms(
    text: str,
    terms: tuple[
        str,
        ...
    ],
) -> tuple[
    str,
    ...
]:
    lowered = text.lower()

    matches = [
        term
        for term in terms
        if term in lowered
    ]

    return tuple(
        matches
    )


# ---------------------------------------------------------------------------
# FIND OXIDE PEROVSKITE FORMULAS
# ---------------------------------------------------------------------------
def find_oxide_perovskite_formulas(
    text: str,
) -> tuple[
    str,
    ...
]:
    normalized = (
        normalize_material_text(
            text
        )
    )

    matches = (
        OXIDE_PEROVSKITE_FORMULA_PATTERN
        .findall(
            normalized
        )
    )

    unique_matches: list[
        str
    ] = []

    for match in matches:
        if match not in unique_matches:
            unique_matches.append(
                match
            )

    return tuple(
        unique_matches
    )


# ---------------------------------------------------------------------------
# DETECT MATERIAL SIGNALS
# ---------------------------------------------------------------------------
def detect_material_signals(
    text: str,
) -> MaterialSignalResult:
    normalized = (
        normalize_material_text(
            text
        )
    )

    perovskite_terms = (
        find_material_terms(
            normalized,
            PEROVSKITE_TERMS,
        )
    )

    perovskite_formulas = (
        find_oxide_perovskite_formulas(
            normalized
        )
    )

    tmd_terms = (
        find_material_terms(
            normalized,
            TMD_TERMS,
        )
    )

    return MaterialSignalResult(
        has_perovskite_signal=bool(
            perovskite_terms
            or perovskite_formulas
        ),
        has_tmd_signal=bool(
            tmd_terms
        ),
        matched_perovskite_terms=(
            perovskite_terms
        ),
        matched_perovskite_formulas=(
            perovskite_formulas
        ),
        matched_tmd_terms=(
            tmd_terms
        ),
    )

