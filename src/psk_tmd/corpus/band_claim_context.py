import re

from psk_tmd.common.constants import (
    BandClaimContext,
)


# ---------------------------------------------------------------------------
# CURRENT-WORK PATTERNS
# ---------------------------------------------------------------------------
CURRENT_WORK_PATTERNS = [
    re.compile(
        r"\bthis\s+(?:work|study)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bthe\s+present\s+(?:work|study)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bin\s+this\s+(?:work|study)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bwe\s+(?:measured|determined|obtained|calculated|estimated|found)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bour\s+(?:results?|measurements?|calculations?|samples?|materials?)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bwas\s+determined\s+in\s+this\s+work\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bwere\s+determined\s+in\s+this\s+work\b",
        flags=re.IGNORECASE,
    ),
]


# ---------------------------------------------------------------------------
# PRIOR-LITERATURE PATTERNS
# ---------------------------------------------------------------------------
PRIOR_LITERATURE_PATTERNS = [
    re.compile(
        r"\bprevious(?:ly)?\s+(?:reported|published|observed|determined)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bprevious\s+(?:studies|reports|work)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bearlier\s+(?:studies|reports|work)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\baccording\s+to\s+(?:the\s+)?literature\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\breported\s+in\s+the\s+literature\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bliterature\s+(?:value|values|data)\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bhas\s+been\s+reported\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\bhave\s+been\s+reported\b",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"\breported\s+by\s+[A-Z][A-Za-z-]+\b",
    ),
]


# ---------------------------------------------------------------------------
# HAS PATTERN MATCH
# ---------------------------------------------------------------------------
def has_pattern_match(
    text: str,
    patterns: list[
        re.Pattern,
    ],
) -> bool:
    return any(
        pattern.search(
            text
        )
        is not None
        for pattern in patterns
    )


# ---------------------------------------------------------------------------
# CLASSIFY BAND CLAIM CONTEXT
# ---------------------------------------------------------------------------
def classify_band_claim_context(
    text: str,
) -> BandClaimContext:
    if not text.strip():
        return (
            BandClaimContext.AMBIGUOUS
        )

    has_current_work = (
        has_pattern_match(
            text,
            CURRENT_WORK_PATTERNS,
        )
    )

    has_prior_literature = (
        has_pattern_match(
            text,
            PRIOR_LITERATURE_PATTERNS,
        )
    )

    if (
        has_current_work
        and not has_prior_literature
    ):
        return (
            BandClaimContext.CURRENT_WORK
        )

    if (
        has_prior_literature
        and not has_current_work
    ):
        return (
            BandClaimContext.PRIOR_LITERATURE
        )

    return (
        BandClaimContext.AMBIGUOUS
    )


