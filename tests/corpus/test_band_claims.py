import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
    BandGapType,
    BandReferenceScale,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_claims import (
    extract_band_claim_candidates,
    find_sentence_span,
    resolve_sentence_band_gap_type,
    resolve_sentence_reference_scale,
)


# ---------------------------------------------------------------------------
# FIND SENTENCE SPAN
# ---------------------------------------------------------------------------
def test_find_sentence_span():
    text = (
        "Previous work reported 2.1 eV. "
        "In this study, Eg = 2.4 eV. "
        "Another sentence follows."
    )

    start = text.index(
        "Eg"
    )

    end = (
        start
        + len(
            "Eg = 2.4 eV"
        )
    )

    (
        sentence_start,
        sentence_end,
    ) = find_sentence_span(
        text,
        start=start,
        end=end,
    )

    sentence = text[
        sentence_start:
        sentence_end
    ]

    assert sentence == (
        "In this study, "
        "Eg = 2.4 eV."
    )


# ---------------------------------------------------------------------------
# CURRENT-WORK BAND GAP CLAIM
# ---------------------------------------------------------------------------
def test_current_work_band_gap_claim():
    text = (
        "In this study, a direct "
        "band gap of 2.35 eV "
        "was obtained."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert len(
        claims
    ) == 1

    claim = claims[
        0
    ]

    assert (
        claim.property_type
        == BandPropertyType.BAND_GAP
    )

    assert (
        claim.numeric_value
        == pytest.approx(
            2.35
        )
    )

    assert (
        claim.claim_context
        == BandClaimContext.CURRENT_WORK
    )

    assert (
        claim.band_gap_type
        == BandGapType.DIRECT
    )


# ---------------------------------------------------------------------------
# PRIOR-LITERATURE CLAIM
# ---------------------------------------------------------------------------
def test_prior_literature_claim():
    text = (
        "Previous studies reported "
        "Eg = 2.10 eV."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert len(
        claims
    ) == 1

    assert (
        claims[
            0
        ].claim_context
        == (
            BandClaimContext
            .PRIOR_LITERATURE
        )
    )


# ---------------------------------------------------------------------------
# DIFFERENT SENTENCES GET DIFFERENT CONTEXTS
# ---------------------------------------------------------------------------
def test_different_sentences_get_different_contexts():
    text = (
        "Previous studies reported "
        "Eg = 2.10 eV. "
        "In this study, we measured "
        "Eg = 2.35 eV."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert len(
        claims
    ) == 2

    assert (
        claims[
            0
        ].claim_context
        == (
            BandClaimContext
            .PRIOR_LITERATURE
        )
    )

    assert (
        claims[
            1
        ].claim_context
        == (
            BandClaimContext
            .CURRENT_WORK
        )
    )


# ---------------------------------------------------------------------------
# NHE REFERENCE SCALE
# ---------------------------------------------------------------------------
def test_nhe_reference_scale():
    text = (
        "In this study, the CBM "
        "was -0.42 V vs NHE."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert len(
        claims
    ) == 1

    assert (
        claims[
            0
        ].property_type
        == BandPropertyType.CBM
    )

    assert (
        claims[
            0
        ].reference_scale
        == BandReferenceScale.NHE
    )


# ---------------------------------------------------------------------------
# AG AGCL REFERENCE SCALE
# ---------------------------------------------------------------------------
def test_ag_agcl_reference_scale():
    text = (
        "We measured ECB = -0.35 V "
        "vs Ag/AgCl."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert (
        claims[
            0
        ].reference_scale
        == (
            BandReferenceScale
            .AG_AGCL
        )
    )


# ---------------------------------------------------------------------------
# MULTIPLE REFERENCE SCALES REMAIN UNRESOLVED
# ---------------------------------------------------------------------------
def test_multiple_reference_scales_are_unresolved():
    text = (
        "The CBM was -0.35 V "
        "vs Ag/AgCl and was later "
        "converted to NHE."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert (
        claims[
            0
        ].reference_scale
        is None
    )


# ---------------------------------------------------------------------------
# DIRECT BAND GAP
# ---------------------------------------------------------------------------
def test_resolve_direct_band_gap():
    result = (
        resolve_sentence_band_gap_type(
            "A direct band gap of "
            "2.1 eV was obtained."
        )
    )

    assert (
        result
        == BandGapType.DIRECT
    )


# ---------------------------------------------------------------------------
# INDIRECT BAND GAP
# ---------------------------------------------------------------------------
def test_resolve_indirect_band_gap():
    result = (
        resolve_sentence_band_gap_type(
            "An indirect transition "
            "was indicated."
        )
    )

    assert (
        result
        == BandGapType.INDIRECT
    )


# ---------------------------------------------------------------------------
# CONFLICTING BAND GAP TYPES REMAIN UNRESOLVED
# ---------------------------------------------------------------------------
def test_conflicting_band_gap_types_are_unresolved():
    result = (
        resolve_sentence_band_gap_type(
            "Both direct band gap and "
            "indirect band gap models "
            "were considered."
        )
    )

    assert result is None


# ---------------------------------------------------------------------------
# RESOLVE REFERENCE SCALE
# ---------------------------------------------------------------------------
def test_resolve_reference_scale():
    result = (
        resolve_sentence_reference_scale(
            "Potential measured "
            "vs RHE."
        )
    )

    assert (
        result
        == BandReferenceScale.RHE
    )


# ---------------------------------------------------------------------------
# SOURCE TEXT IS PRESERVED
# ---------------------------------------------------------------------------
def test_source_text_is_preserved():
    text = (
        "Introduction statement. "
        "We measured Eg = 2.30 eV. "
        "Final statement."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert (
        claims[
            0
        ].source_text
        == "We measured Eg = 2.30 eV."
    )


# ---------------------------------------------------------------------------
# NONNUMERIC CANDIDATES DO NOT BECOME CLAIMS
# ---------------------------------------------------------------------------
def test_nonnumeric_candidates_do_not_become_claims():
    text = (
        "The material exhibits a "
        "direct band gap and the "
        "values are referenced to NHE."
    )

    claims = (
        extract_band_claim_candidates(
            text
        )
    )

    assert claims == []

