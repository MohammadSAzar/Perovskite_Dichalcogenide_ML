import re

from dataclasses import dataclass

from psk_tmd.common.constants import (
    BandClaimContext,
    BandGapType,
    BandReferenceScale,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyCandidate,
    BandPropertyType,
    extract_band_gap_type_candidates,
    extract_band_property_candidates,
    extract_reference_scale_candidates,
)
from psk_tmd.corpus.band_claim_context import (
    classify_band_claim_context,
)


# ---------------------------------------------------------------------------
# BAND CLAIM CANDIDATE
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BandClaimCandidate:
    property_type: BandPropertyType
    numeric_value: float
    matched_text: str
    source_text: str
    start: int
    end: int
    claim_context: BandClaimContext
    band_gap_type: BandGapType | None = None
    reference_scale: BandReferenceScale | None = None


# ---------------------------------------------------------------------------
# FIND SENTENCE SPAN
# ---------------------------------------------------------------------------
def find_sentence_span(
    text: str,
    *,
    start: int,
    end: int,
) -> tuple[
    int,
    int,
]:
    if start < 0 or end > len(
        text
    ):
        raise ValueError(
            "Candidate offsets are "
            "outside the text."
        )

    if start >= end:
        raise ValueError(
            "Candidate start must be "
            "smaller than end."
        )

    left_boundary = 0

    for match in re.finditer(
        r"[.!?\n]",
        text[
            :start
        ],
    ):
        left_boundary = (
            match.end()
        )

    right_match = re.search(
        r"[.!?\n]",
        text[
            end:
        ],
    )

    if right_match is None:
        right_boundary = len(
            text
        )
    else:
        right_boundary = (
            end
            + right_match.end()
        )

    while (
        left_boundary
        < right_boundary
        and text[
            left_boundary
        ].isspace()
    ):
        left_boundary += 1

    while (
        right_boundary
        > left_boundary
        and text[
            right_boundary - 1
        ].isspace()
    ):
        right_boundary -= 1

    return (
        left_boundary,
        right_boundary,
    )


# ---------------------------------------------------------------------------
# RESOLVE BAND GAP TYPE
# ---------------------------------------------------------------------------
def resolve_sentence_band_gap_type(
    sentence: str,
) -> BandGapType | None:
    candidates = (
        extract_band_gap_type_candidates(
            sentence
        )
    )

    values = {
        candidate.normalized_value
        for candidate in candidates
        if candidate.normalized_value
        is not None
    }

    if len(
        values
    ) != 1:
        return None

    value = next(
        iter(
            values
        )
    )

    if value == "direct":
        return (
            BandGapType.DIRECT
        )

    if value == "indirect":
        return (
            BandGapType.INDIRECT
        )

    return None


# ---------------------------------------------------------------------------
# RESOLVE REFERENCE SCALE
# ---------------------------------------------------------------------------
def resolve_sentence_reference_scale(
    sentence: str,
) -> BandReferenceScale | None:
    candidates = (
        extract_reference_scale_candidates(
            sentence
        )
    )

    values = {
        candidate.normalized_value
        for candidate in candidates
        if candidate.normalized_value
        is not None
    }

    if len(
        values
    ) != 1:
        return None

    value = next(
        iter(
            values
        )
    )

    return BandReferenceScale(
        value
    )


# ---------------------------------------------------------------------------
# BUILD BAND CLAIM
# ---------------------------------------------------------------------------
def build_band_claim_candidate(
    text: str,
    candidate: BandPropertyCandidate,
) -> BandClaimCandidate:
    if candidate.numeric_value is None:
        raise ValueError(
            "Band claim candidate must "
            "contain a numeric value."
        )

    (
        sentence_start,
        sentence_end,
    ) = find_sentence_span(
        text,
        start=candidate.start,
        end=candidate.end,
    )

    sentence = text[
        sentence_start:
        sentence_end
    ]

    claim_context = (
        classify_band_claim_context(
            sentence
        )
    )

    band_gap_type = None

    if (
        candidate.property_type
        == BandPropertyType.BAND_GAP
    ):
        band_gap_type = (
            resolve_sentence_band_gap_type(
                sentence
            )
        )

    reference_scale = (
        resolve_sentence_reference_scale(
            sentence
        )
    )

    return (
        BandClaimCandidate(
            property_type=(
                candidate.property_type
            ),
            numeric_value=(
                candidate.numeric_value
            ),
            matched_text=(
                candidate.matched_text
            ),
            source_text=sentence,
            start=candidate.start,
            end=candidate.end,
            claim_context=(
                claim_context
            ),
            band_gap_type=(
                band_gap_type
            ),
            reference_scale=(
                reference_scale
            ),
        )
    )


# ---------------------------------------------------------------------------
# EXTRACT BAND CLAIMS
# ---------------------------------------------------------------------------
def extract_band_claim_candidates(
    text: str,
) -> list[
    BandClaimCandidate
]:
    raw_candidates = (
        extract_band_property_candidates(
            text
        )
    )

    numeric_candidates = [
        candidate
        for candidate in raw_candidates
        if candidate.numeric_value
        is not None
    ]

    return [
        build_band_claim_candidate(
            text,
            candidate,
        )
        for candidate in numeric_candidates
    ]

