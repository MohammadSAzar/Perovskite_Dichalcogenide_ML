import re
from enum import Enum

from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    MechanismLabel,
)
from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# CARRIER PATHWAY TYPE
# ---------------------------------------------------------------------------
class CarrierPathwayType(str, Enum):
    TYPE_II_LIKE = "type_ii_like"

    MEDIATED_RECOMBINATION_LIKE = (
        "mediated_recombination_like"
    )

    CONFLICTING = "conflicting"

    UNRESOLVED = "unresolved"


# ---------------------------------------------------------------------------
# MECHANISM CONSISTENCY STATUS
# ---------------------------------------------------------------------------
class MechanismConsistencyStatus(
    str,
    Enum,
):
    CONSISTENT = "consistent"

    POTENTIALLY_INCONSISTENT = (
        "potentially_inconsistent"
    )

    INTERNALLY_CONFLICTING = (
        "internally_conflicting"
    )

    INSUFFICIENT_INFORMATION = (
        "insufficient_information"
    )


# ---------------------------------------------------------------------------
# MECHANISM CONSISTENCY RESULT
# ---------------------------------------------------------------------------
class MechanismConsistencyResult(
    BaseModel
):
    reported_mechanism: MechanismLabel

    pathway_type: CarrierPathwayType = (
        CarrierPathwayType.UNRESOLVED
    )

    consistency_status: (
        MechanismConsistencyStatus
    ) = (
        MechanismConsistencyStatus
        .INSUFFICIENT_INFORMATION
    )

    matched_patterns: list[str] = Field(
        default_factory=list,
    )

    source_text: str | None = None


# ---------------------------------------------------------------------------
# NORMALIZE MECHANISM TEXT
# ---------------------------------------------------------------------------
def normalize_mechanism_text(
    text: str,
) -> str:
    clean_text = text.replace(
        "\u00ad",
        "",
    )

    clean_text = re.sub(
        r"(\w)-\s+(\w)",
        r"\1\2",
        clean_text,
    )

    return normalize_whitespace(
        clean_text
    )


# ---------------------------------------------------------------------------
# TYPE-II-LIKE PATTERNS
# ---------------------------------------------------------------------------
TYPE_II_LIKE_PATTERNS: tuple[
    re.Pattern[str],
    ...,
] = (
    re.compile(
        r"electrons?"
        r".{0,160}"
        r"(?:transfer|move|migrate)"
        r".{0,160}"
        r"(?:conduction\s+band|\bCB\b)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"electrons?"
        r".{0,160}"
        r"(?:conduction\s+band|\bCB\b)"
        r".{0,160}"
        r"(?:transfer|move|migrate)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"holes?"
        r".{0,160}"
        r"(?:transfer|move|migrate)"
        r".{0,160}"
        r"(?:valence\s+band|\bVB\b)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"holes?"
        r".{0,160}"
        r"(?:valence\s+band|\bVB\b)"
        r".{0,160}"
        r"(?:transfer|move|migrate)",
        flags=re.IGNORECASE,
    ),
)


# ---------------------------------------------------------------------------
# GENERAL CARRIER-TRANSFER PATTERNS
# ---------------------------------------------------------------------------
ELECTRON_TRANSFER_PATTERN = re.compile(
    r"electrons?"
    r".{0,180}"
    r"(?:transfer|move|migrate)"
    r".{0,180}"
    r"(?:from|to)",
    flags=re.IGNORECASE,
)


HOLE_TRANSFER_PATTERN = re.compile(
    r"holes?"
    r".{0,180}"
    r"(?:transfer|move|migrate)"
    r".{0,180}"
    r"(?:from|to)",
    flags=re.IGNORECASE,
)


BAND_CONTEXT_PATTERN = re.compile(
    r"(?:"
    r"conduction\s+band"
    r"|valence\s+band"
    r"|\bCB\b"
    r"|\bVB\b"
    r")",
    flags=re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# MEDIATED-RECOMBINATION-LIKE PATTERNS
# ---------------------------------------------------------------------------
MEDIATED_RECOMBINATION_PATTERNS: tuple[
    re.Pattern[str],
    ...,
] = (
    re.compile(
        r"recombination"
        r".{0,120}"
        r"electrons?"
        r".{0,120}"
        r"(?:conduction\s+band|\bCB\b)"
        r".{0,160}"
        r"holes?"
        r".{0,120}"
        r"(?:valence\s+band|\bVB\b)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"electrons?"
        r".{0,120}"
        r"(?:conduction\s+band|\bCB\b)"
        r".{0,160}"
        r"recombin(?:e|es|ed|ing|ation)"
        r".{0,160}"
        r"holes?"
        r".{0,120}"
        r"(?:valence\s+band|\bVB\b)",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"electrons?"
        r".{0,120}"
        r"(?:conduction\s+band|\bCB\b)"
        r".{0,160}"
        r"holes?"
        r".{0,120}"
        r"(?:valence\s+band|\bVB\b)"
        r".{0,160}"
        r"recombin(?:e|es|ed|ing|ation)",
        flags=re.IGNORECASE,
    ),
)


# ---------------------------------------------------------------------------
# SELECTIVE-CARRIER EQUATION PATTERNS
# ---------------------------------------------------------------------------
SELECTIVE_CARRIER_EQUATION_PATTERNS: tuple[
    re.Pattern[str],
    ...,
] = (
    re.compile(
        r"\([^)]*e\s*[−\-]"
        r"[^)]*h\s*\+[^)]*\)"
        r".{0,160}"
        r"(?:→|->)"
        r".{0,160}"
        r"\([^)]*e\s*[−\-][^)]*\)"
        r".{0,160}"
        r"\([^)]*h\s*\+[^)]*\)",
        flags=re.IGNORECASE,
    ),
)


# ---------------------------------------------------------------------------
# FIND MATCHED PATTERNS
# ---------------------------------------------------------------------------
def find_pattern_matches(
    text: str,
    patterns: tuple[
        re.Pattern[str],
        ...,
    ],
) -> list[str]:
    clean_text = (
        normalize_mechanism_text(
            text
        )
    )

    matches: list[str] = []

    for pattern in patterns:
        match = pattern.search(
            clean_text
        )

        if match is not None:
            matches.append(
                match.group(0)
            )

    return matches


# ---------------------------------------------------------------------------
# FIND TYPE-II-LIKE SIGNALS
# ---------------------------------------------------------------------------
def find_type_ii_like_matches(
    text: str,
) -> list[str]:
    clean_text = (
        normalize_mechanism_text(
            text
        )
    )

    explicit_matches = (
        find_pattern_matches(
            clean_text,
            TYPE_II_LIKE_PATTERNS,
        )
    )

    electron_match = (
        ELECTRON_TRANSFER_PATTERN.search(
            clean_text
        )
    )

    hole_match = (
        HOLE_TRANSFER_PATTERN.search(
            clean_text
        )
    )

    has_band_context = (
        BAND_CONTEXT_PATTERN.search(
            clean_text
        )
        is not None
    )

    matches = list(
        explicit_matches
    )

    if (
        electron_match is not None
        and electron_match.group(0)
        not in matches
    ):
        matches.append(
            electron_match.group(0)
        )

    if (
        hole_match is not None
        and hole_match.group(0)
        not in matches
    ):
        matches.append(
            hole_match.group(0)
        )

    if (
        electron_match is not None
        and hole_match is not None
        and has_band_context
    ):
        return matches

    if len(
        explicit_matches
    ) >= 2:
        return matches

    return []


# ---------------------------------------------------------------------------
# CLASSIFY CARRIER PATHWAY
# ---------------------------------------------------------------------------
def classify_carrier_pathway(
    text: str,
) -> tuple[
    CarrierPathwayType,
    list[str],
]:
    mediated_matches = (
        find_pattern_matches(
            text,
            MEDIATED_RECOMBINATION_PATTERNS,
        )
    )

    equation_matches = (
        find_pattern_matches(
            text,
            SELECTIVE_CARRIER_EQUATION_PATTERNS,
        )
    )

    mediated_matches.extend(
        equation_matches
    )

    type_ii_matches = (
        find_type_ii_like_matches(
            text
        )
    )

    has_mediated_signal = bool(
        mediated_matches
    )

    has_type_ii_signal = bool(
        type_ii_matches
    )

    if (
        has_mediated_signal
        and has_type_ii_signal
    ):
        return (
            CarrierPathwayType.CONFLICTING,
            (
                type_ii_matches
                + mediated_matches
            ),
        )

    if has_mediated_signal:
        return (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE,
            mediated_matches,
        )

    if has_type_ii_signal:
        return (
            CarrierPathwayType.TYPE_II_LIKE,
            type_ii_matches,
        )

    return (
        CarrierPathwayType.UNRESOLVED,
        [],
    )


# ---------------------------------------------------------------------------
# CHECK MECHANISM CONSISTENCY
# ---------------------------------------------------------------------------
def check_mechanism_consistency(
    reported_mechanism: MechanismLabel,
    source_text: str,
) -> MechanismConsistencyResult:
    (
        pathway_type,
        matched_patterns,
    ) = classify_carrier_pathway(
        source_text
    )

    if (
        pathway_type
        == CarrierPathwayType.UNRESOLVED
    ):
        status = (
            MechanismConsistencyStatus
            .INSUFFICIENT_INFORMATION
        )

    elif (
        pathway_type
        == CarrierPathwayType.CONFLICTING
    ):
        status = (
            MechanismConsistencyStatus
            .INTERNALLY_CONFLICTING
        )

    elif (
        reported_mechanism
        in {
            MechanismLabel.Z_SCHEME,
            MechanismLabel.S_SCHEME,
        }
        and pathway_type
        == CarrierPathwayType.TYPE_II_LIKE
    ):
        status = (
            MechanismConsistencyStatus
            .POTENTIALLY_INCONSISTENT
        )

    elif (
        reported_mechanism
        in {
            MechanismLabel.Z_SCHEME,
            MechanismLabel.S_SCHEME,
        }
        and pathway_type
        == (
            CarrierPathwayType
            .MEDIATED_RECOMBINATION_LIKE
        )
    ):
        status = (
            MechanismConsistencyStatus
            .CONSISTENT
        )

    elif (
        reported_mechanism
        == MechanismLabel.TYPE_II
        and pathway_type
        == CarrierPathwayType.TYPE_II_LIKE
    ):
        status = (
            MechanismConsistencyStatus
            .CONSISTENT
        )

    else:
        status = (
            MechanismConsistencyStatus
            .INSUFFICIENT_INFORMATION
        )

    return MechanismConsistencyResult(
        reported_mechanism=(
            reported_mechanism
        ),
        pathway_type=pathway_type,
        consistency_status=status,
        matched_patterns=(
            matched_patterns
        ),
        source_text=source_text,
    )

