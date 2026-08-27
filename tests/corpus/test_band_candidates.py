import pytest

from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
    extract_band_gap_candidates,
    extract_band_gap_type_candidates,
    extract_band_property_candidates,
    extract_cbm_candidates,
    extract_reference_scale_candidates,
    extract_vbm_candidates,
)


# ---------------------------------------------------------------------------
# BAND GAP
# ---------------------------------------------------------------------------
def test_extract_band_gap():
    text = (
        "The band gap was 2.45 eV."
    )

    candidates = (
        extract_band_gap_candidates(
            text
        )
    )

    assert len(
        candidates
    ) == 1

    assert (
        candidates[
            0
        ].property_type
        == BandPropertyType.BAND_GAP
    )

    assert (
        candidates[
            0
        ].numeric_value
        == pytest.approx(
            2.45
        )
    )


# ---------------------------------------------------------------------------
# EG TERMINOLOGY
# ---------------------------------------------------------------------------
def test_extract_eg_terminology():
    text = (
        "Eg = 1.82 eV, while "
        "E_g = 2.10 eV."
    )

    candidates = (
        extract_band_gap_candidates(
            text
        )
    )

    assert [
        candidate.numeric_value
        for candidate in candidates
    ] == pytest.approx(
        [
            1.82,
            2.10,
        ]
    )


# ---------------------------------------------------------------------------
# CBM TERMINOLOGY
# ---------------------------------------------------------------------------
def test_extract_cbm():
    text = (
        "The CBM was -0.42 V and "
        "ECB = -0.35 V."
    )

    candidates = (
        extract_cbm_candidates(
            text
        )
    )

    assert [
        candidate.numeric_value
        for candidate in candidates
    ] == pytest.approx(
        [
            -0.42,
            -0.35,
        ]
    )


# ---------------------------------------------------------------------------
# VBM TERMINOLOGY
# ---------------------------------------------------------------------------
def test_extract_vbm():
    text = (
        "The VBM is 2.31 V, while "
        "EVB = 2.40 V."
    )

    candidates = (
        extract_vbm_candidates(
            text
        )
    )

    assert [
        candidate.numeric_value
        for candidate in candidates
    ] == pytest.approx(
        [
            2.31,
            2.40,
        ]
    )


# ---------------------------------------------------------------------------
# LONG BAND EDGE TERMINOLOGY
# ---------------------------------------------------------------------------
def test_extract_long_band_edge_terms():
    text = (
        "The conduction band minimum "
        "was -0.55 V and the valence "
        "band maximum was 1.85 V."
    )

    cbm = extract_cbm_candidates(
        text
    )

    vbm = extract_vbm_candidates(
        text
    )

    assert (
        cbm[
            0
        ].numeric_value
        == pytest.approx(
            -0.55
        )
    )

    assert (
        vbm[
            0
        ].numeric_value
        == pytest.approx(
            1.85
        )
    )


# ---------------------------------------------------------------------------
# DIRECT BAND GAP
# ---------------------------------------------------------------------------
def test_extract_direct_band_gap():
    text = (
        "The material exhibits a "
        "direct band gap."
    )

    candidates = (
        extract_band_gap_type_candidates(
            text
        )
    )

    assert len(
        candidates
    ) == 1

    assert (
        candidates[
            0
        ].normalized_value
        == "direct"
    )


# ---------------------------------------------------------------------------
# INDIRECT TRANSITION
# ---------------------------------------------------------------------------
def test_extract_indirect_transition():
    text = (
        "An indirect transition "
        "was obtained from the "
        "Tauc analysis."
    )

    candidates = (
        extract_band_gap_type_candidates(
            text
        )
    )

    assert (
        candidates[
            0
        ].normalized_value
        == "indirect"
    )


# ---------------------------------------------------------------------------
# REFERENCE SCALES
# ---------------------------------------------------------------------------
def test_extract_reference_scales():
    text = (
        "Potentials were reported "
        "vs Ag/AgCl and converted "
        "to NHE. RHE values were "
        "also discussed."
    )

    candidates = (
        extract_reference_scale_candidates(
            text
        )
    )

    assert [
        candidate.normalized_value
        for candidate in candidates
    ] == [
        "ag_agcl",
        "nhe",
        "rhe",
    ]


# ---------------------------------------------------------------------------
# VACUUM SCALE
# ---------------------------------------------------------------------------
def test_extract_vacuum_scale():
    text = (
        "The band edges were aligned "
        "to the vacuum level."
    )

    candidates = (
        extract_reference_scale_candidates(
            text
        )
    )

    assert len(
        candidates
    ) == 1

    assert (
        candidates[
            0
        ].normalized_value
        == "vacuum"
    )


# ---------------------------------------------------------------------------
# EXTRACT ALL CANDIDATES
# ---------------------------------------------------------------------------
def test_extract_all_candidates():
    text = (
        "A direct band gap of "
        "2.10 eV was obtained. "
        "The CBM = -0.45 V and "
        "VBM = 1.65 V vs NHE."
    )

    candidates = (
        extract_band_property_candidates(
            text
        )
    )

    property_types = [
        candidate.property_type
        for candidate in candidates
    ]

    assert (
        BandPropertyType.BAND_GAP
        in property_types
    )

    assert (
        BandPropertyType.CBM
        in property_types
    )

    assert (
        BandPropertyType.VBM
        in property_types
    )

    assert (
        BandPropertyType.BAND_GAP_TYPE
        in property_types
    )

    assert (
        BandPropertyType.REFERENCE_SCALE
        in property_types
    )


# ---------------------------------------------------------------------------
# CANDIDATES KEEP TEXT OFFSETS
# ---------------------------------------------------------------------------
def test_candidates_keep_text_offsets():
    text = (
        "Measured Eg = 2.30 eV."
    )

    candidate = (
        extract_band_gap_candidates(
            text
        )[
            0
        ]
    )

    assert (
        text[
            candidate.start:
            candidate.end
        ]
        == candidate.matched_text
    )


# ---------------------------------------------------------------------------
# NO FALSE NUMERIC EXTRACTION WITHOUT TERM
# ---------------------------------------------------------------------------
def test_number_without_band_term_is_ignored():
    text = (
        "The sample was heated "
        "at 500 C for 2 h."
    )

    candidates = (
        extract_band_property_candidates(
            text
        )
    )

    assert candidates == []

