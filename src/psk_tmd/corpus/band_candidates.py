import re

from dataclasses import dataclass
from enum import Enum


# ---------------------------------------------------------------------------
# BAND PROPERTY TYPE
# ---------------------------------------------------------------------------
class BandPropertyType(str, Enum):
    BAND_GAP = "band_gap"
    CBM = "cbm"
    VBM = "vbm"
    BAND_GAP_TYPE = "band_gap_type"
    REFERENCE_SCALE = "reference_scale"


# ---------------------------------------------------------------------------
# BAND PROPERTY CANDIDATE
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BandPropertyCandidate:
    property_type: BandPropertyType
    matched_text: str
    start: int
    end: int
    numeric_value: float | None = None
    normalized_value: str | None = None


# ---------------------------------------------------------------------------
# NUMERIC PATTERN
# ---------------------------------------------------------------------------
NUMERIC_PATTERN = (
    r"[-+]?"
    r"(?:\d+(?:\.\d+)?|\.\d+)"
)


# ---------------------------------------------------------------------------
# BAND GAP PATTERNS
# ---------------------------------------------------------------------------
BAND_GAP_PATTERNS = [
    re.compile(
        rf"\b(?:band\s*gap|E[_\s]*g)\b"
        rf"\s*(?:=|:|of|is|was|were)?\s*"
        rf"(?P<value>{NUMERIC_PATTERN})"
        rf"\s*(?:eV)\b",
        flags=re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# CBM PATTERNS
# ---------------------------------------------------------------------------
CBM_PATTERNS = [
    re.compile(
        rf"\b"
        rf"(?:"
        rf"CBM"
        rf"|E[_\s]*CB"
        rf"|conduction\s+band\s+minimum"
        rf"|conduction\s+band\s+edge"
        rf")"
        rf"\b"
        rf"\s*(?:=|:|of|is|was|were|at)?\s*"
        rf"(?P<value>{NUMERIC_PATTERN})"
        rf"\s*(?:V|eV)\b",
        flags=re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# VBM PATTERNS
# ---------------------------------------------------------------------------
VBM_PATTERNS = [
    re.compile(
        rf"\b"
        rf"(?:"
        rf"VBM"
        rf"|E[_\s]*VB"
        rf"|valence\s+band\s+maximum"
        rf"|valence\s+band\s+edge"
        rf")"
        rf"\b"
        rf"\s*(?:=|:|of|is|was|were|at)?\s*"
        rf"(?P<value>{NUMERIC_PATTERN})"
        rf"\s*(?:V|eV)\b",
        flags=re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# BAND GAP TYPE PATTERNS
# ---------------------------------------------------------------------------
BAND_GAP_TYPE_PATTERNS = [
    (
        re.compile(
            r"\bdirect\s+(?:band\s*)?gap\b",
            flags=re.IGNORECASE,
        ),
        "direct",
    ),
    (
        re.compile(
            r"\bindirect\s+(?:band\s*)?gap\b",
            flags=re.IGNORECASE,
        ),
        "indirect",
    ),
    (
        re.compile(
            r"\bdirect\s+transition\b",
            flags=re.IGNORECASE,
        ),
        "direct",
    ),
    (
        re.compile(
            r"\bindirect\s+transition\b",
            flags=re.IGNORECASE,
        ),
        "indirect",
    ),
]


# ---------------------------------------------------------------------------
# REFERENCE SCALE PATTERNS
# ---------------------------------------------------------------------------
REFERENCE_SCALE_PATTERNS = [
    (
        re.compile(
            r"\bNHE\b",
            flags=re.IGNORECASE,
        ),
        "nhe",
    ),
    (
        re.compile(
            r"\bSHE\b",
            flags=re.IGNORECASE,
        ),
        "she",
    ),
    (
        re.compile(
            r"\bRHE\b",
            flags=re.IGNORECASE,
        ),
        "rhe",
    ),
    (
        re.compile(
            r"\bAg\s*/\s*AgCl\b",
            flags=re.IGNORECASE,
        ),
        "ag_agcl",
    ),
    (
        re.compile(
            r"\bSCE\b",
            flags=re.IGNORECASE,
        ),
        "sce",
    ),
    (
        re.compile(
            r"\bvacuum(?:\s+level|\s+scale)?\b",
            flags=re.IGNORECASE,
        ),
        "vacuum",
    ),
]


# ---------------------------------------------------------------------------
# EXTRACT NUMERIC CANDIDATES
# ---------------------------------------------------------------------------
def extract_numeric_candidates(
    text: str,
    *,
    property_type: BandPropertyType,
    patterns: list[
        re.Pattern,
    ],
) -> list[
    BandPropertyCandidate
]:
    candidates: list[
        BandPropertyCandidate
    ] = []

    for pattern in patterns:
        for match in pattern.finditer(
            text
        ):
            value = float(
                match.group(
                    "value"
                )
            )

            candidates.append(
                BandPropertyCandidate(
                    property_type=(
                        property_type
                    ),
                    matched_text=(
                        match.group(
                            0
                        )
                    ),
                    start=match.start(),
                    end=match.end(),
                    numeric_value=value,
                )
            )

    return candidates


# ---------------------------------------------------------------------------
# EXTRACT BAND GAP CANDIDATES
# ---------------------------------------------------------------------------
def extract_band_gap_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    return extract_numeric_candidates(
        text,
        property_type=(
            BandPropertyType.BAND_GAP
        ),
        patterns=BAND_GAP_PATTERNS,
    )


# ---------------------------------------------------------------------------
# EXTRACT CBM CANDIDATES
# ---------------------------------------------------------------------------
def extract_cbm_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    return extract_numeric_candidates(
        text,
        property_type=(
            BandPropertyType.CBM
        ),
        patterns=CBM_PATTERNS,
    )


# ---------------------------------------------------------------------------
# EXTRACT VBM CANDIDATES
# ---------------------------------------------------------------------------
def extract_vbm_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    return extract_numeric_candidates(
        text,
        property_type=(
            BandPropertyType.VBM
        ),
        patterns=VBM_PATTERNS,
    )


# ---------------------------------------------------------------------------
# EXTRACT BAND GAP TYPE CANDIDATES
# ---------------------------------------------------------------------------
def extract_band_gap_type_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    candidates: list[
        BandPropertyCandidate
    ] = []

    for (
        pattern,
        normalized_value,
    ) in BAND_GAP_TYPE_PATTERNS:
        for match in pattern.finditer(
            text
        ):
            candidates.append(
                BandPropertyCandidate(
                    property_type=(
                        BandPropertyType
                        .BAND_GAP_TYPE
                    ),
                    matched_text=(
                        match.group(
                            0
                        )
                    ),
                    start=match.start(),
                    end=match.end(),
                    normalized_value=(
                        normalized_value
                    ),
                )
            )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.start,
            candidate.end,
        ),
    )


# ---------------------------------------------------------------------------
# EXTRACT REFERENCE SCALE CANDIDATES
# ---------------------------------------------------------------------------
def extract_reference_scale_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    candidates: list[
        BandPropertyCandidate
    ] = []

    for (
        pattern,
        normalized_value,
    ) in REFERENCE_SCALE_PATTERNS:
        for match in pattern.finditer(
            text
        ):
            candidates.append(
                BandPropertyCandidate(
                    property_type=(
                        BandPropertyType
                        .REFERENCE_SCALE
                    ),
                    matched_text=(
                        match.group(
                            0
                        )
                    ),
                    start=match.start(),
                    end=match.end(),
                    normalized_value=(
                        normalized_value
                    ),
                )
            )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.start,
            candidate.end,
        ),
    )


# ---------------------------------------------------------------------------
# EXTRACT ALL BAND PROPERTY CANDIDATES
# ---------------------------------------------------------------------------
def extract_band_property_candidates(
    text: str,
) -> list[
    BandPropertyCandidate
]:
    candidates = (
        extract_band_gap_candidates(
            text
        )
        + extract_cbm_candidates(
            text
        )
        + extract_vbm_candidates(
            text
        )
        + extract_band_gap_type_candidates(
            text
        )
        + extract_reference_scale_candidates(
            text
        )
    )

    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.start,
            candidate.end,
        ),
    )

