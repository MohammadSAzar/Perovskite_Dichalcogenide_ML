import pytest

from psk_tmd.common.constants import (
    BandGapType,
    MaterialType,
    BandReferenceScale,
    BandClaimContext,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_structured_extraction import (
    extract_structured_band_values,
    normalize_pdf_numeric_text,
)


# ---------------------------------------------------------------------------
# BUILD RASHKI PAIR
# ---------------------------------------------------------------------------
def make_rashki_pair() -> PairRecord:
    return (
        PairRecord(
            pair_id="PAIR-0004",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="WS2",
            tmd_formula_normalized="WS2",
        )
    )


# ---------------------------------------------------------------------------
# BUILD MAO PAIR
# ---------------------------------------------------------------------------
def make_mao_pair() -> PairRecord:
    return (
        PairRecord(
            pair_id="PAIR-0002",
            psk_formula_reported="LaNiO3",
            psk_formula_normalized="LaNiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )


# ---------------------------------------------------------------------------
# BUILD QIN PAIR
# ---------------------------------------------------------------------------
def make_qin_pair() -> PairRecord:
    return (
        PairRecord(
            pair_id="PAIR-0001",
            psk_formula_reported="PbTiO3",
            psk_formula_normalized="PbTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )


# ---------------------------------------------------------------------------
# NORMALIZE PDF MINUS ARTIFACT
# ---------------------------------------------------------------------------
def test_normalize_pdf_minus_artifact():
    result = (
        normalize_pdf_numeric_text(
            "ظêْ0.29"
        )
    )

    assert result == "-0.29"


# ---------------------------------------------------------------------------
# MAO BAND GAP RESPECTIVELY
# ---------------------------------------------------------------------------
def test_mao_band_gap_respectively():
    text = (
        "The Eg of LaNiO3 and MoS2 "
        "are given in Fig. 9b, which "
        "are 2.54 eV and 1.92 eV, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_mao_pair(),
        )
    )

    gaps = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.BAND_GAP
    ]

    assert len(
        gaps
    ) == 2

    assert (
        gaps[
            0
        ].formula
        == "LaNiO3"
    )

    assert (
        gaps[
            0
        ].numeric_value
        == pytest.approx(
            2.54
        )
    )

    assert (
        gaps[
            1
        ].formula
        == "MoS2"
    )

    assert (
        gaps[
            1
        ].numeric_value
        == pytest.approx(
            1.92
        )
    )


# ---------------------------------------------------------------------------
# RASHKI HETEROSTRUCTURE GAP IS SKIPPED
# ---------------------------------------------------------------------------
def test_rashki_heterostructure_gap_is_skipped():
    text = (
        "The band gap energies of the "
        "CaTiO3 nanoparticles, the "
        "Z-scheme CaTiO3/WS2 "
        "heterostructure and WS2 are "
        "calculated to be 3.45, 2.71 "
        "and 1.82 eV, respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_rashki_pair(),
        )
    )

    gaps = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.BAND_GAP
    ]

    assert len(
        gaps
    ) == 2

    assert {
        value.formula:
        value.numeric_value
        for value in gaps
    } == pytest.approx(
        {
            "CaTiO3": 3.45,
            "WS2": 1.82,
        }
    )


# ---------------------------------------------------------------------------
# RASHKI CB RESPECTIVELY
# ---------------------------------------------------------------------------
def test_rashki_cb_respectively():
    text = (
        "The conduction band (CB) "
        "potentials of CaTiO3 and WS2 "
        "samples are determined to be "
        "ظêْ0.29 and ظêْ0.44 "
        "(vs NHE), respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_rashki_pair(),
        )
    )

    cb_values = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.CBM
    ]

    assert len(
        cb_values
    ) == 2

    assert {
        value.formula:
        value.numeric_value
        for value in cb_values
    } == pytest.approx(
        {
            "CaTiO3": -0.29,
            "WS2": -0.44,
        }
    )


# ---------------------------------------------------------------------------
# QIN BAND GAP VALUE FOR FORMULA
# ---------------------------------------------------------------------------
def test_qin_band_gap_value_for_formula():
    text = (
        "The band gap is 1.85 eV for "
        "MoS2 and 3.07 eV for PbTiO3."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_qin_pair(),
        )
    )

    gaps = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.BAND_GAP
    ]

    assert {
        value.formula:
        value.numeric_value
        for value in gaps
    } == pytest.approx(
        {
            "MoS2": 1.85,
            "PbTiO3": 3.07,
        }
    )


# ---------------------------------------------------------------------------
# QIN CB PARENTHETICAL FORMULAS
# ---------------------------------------------------------------------------
def test_qin_cb_parenthetical_formulas():
    text = (
        "The energy levels of CB of "
        "PbTiO3 and MoS2 composites "
        "can be calculated, and they "
        "are ظêْ1.20 eV (PbTiO3) and "
        "ظêْ1.65 eV (MoS2), "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_qin_pair(),
        )
    )

    cb_values = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.CBM
    ]

    assert {
        value.formula:
        value.numeric_value
        for value in cb_values
    } == pytest.approx(
        {
            "PbTiO3": -1.20,
            "MoS2": -1.65,
        }
    )


# ---------------------------------------------------------------------------
# DIRECT AND INDIRECT ARE MATERIAL SPECIFIC
# ---------------------------------------------------------------------------
def test_direct_indirect_material_specific():
    text = (
        "The indirect band gap feature "
        "of CaTiO3 was used in the "
        "Tauc analysis. The direct "
        "band gap characteristic of "
        "WS2 was also evaluated. "
        "The band gap energies of "
        "CaTiO3 and WS2 are calculated "
        "to be 3.45 and 1.82 eV, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_rashki_pair(),
        )
    )

    gaps = {
        value.formula:
        value
        for value in values
        if value.property_type
        == BandPropertyType.BAND_GAP
    }

    assert (
        gaps[
            "CaTiO3"
        ].band_gap_type
        == BandGapType.INDIRECT
    )

    assert (
        gaps[
            "WS2"
        ].band_gap_type
        == BandGapType.DIRECT
    )


# ---------------------------------------------------------------------------
# MATERIAL TYPES ARE PRESERVED
# ---------------------------------------------------------------------------
def test_material_types_are_preserved():
    text = (
        "The Eg of LaNiO3 and MoS2 "
        "are given in Fig. 9b, which "
        "are 2.54 eV and 1.92 eV, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_mao_pair(),
        )
    )

    by_formula = {
        value.formula:
        value.material_type
        for value in values
    }

    assert (
        by_formula[
            "LaNiO3"
        ]
        == MaterialType.PSK
    )

    assert (
        by_formula[
            "MoS2"
        ]
        == MaterialType.TMD
    )


# ---------------------------------------------------------------------------
# MAO CB AND VB PAIRS
# ---------------------------------------------------------------------------
def test_mao_cb_vb_pairs():
    text = (
        "Based on the above formula and "
        "data, it is concluded that CB "
        "and VB of LaNiO3 are - 0.1 eV "
        "and 2.44 eV, and CB and VB of "
        "MoS2 are - 0.04 eV and "
        "2.04 eV, respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_mao_pair(),
        )
    )

    extracted = {
        (
            value.formula,
            value.property_type,
        ):
        value.numeric_value
        for value in values
    }

    assert extracted[
        (
            "LaNiO3",
            BandPropertyType.CBM,
        )
    ] == pytest.approx(
        -0.10
    )

    assert extracted[
        (
            "LaNiO3",
            BandPropertyType.VBM,
        )
    ] == pytest.approx(
        2.44
    )

    assert extracted[
        (
            "MoS2",
            BandPropertyType.CBM,
        )
    ] == pytest.approx(
        -0.04
    )

    assert extracted[
        (
            "MoS2",
            BandPropertyType.VBM,
        )
    ] == pytest.approx(
        2.04
    )


# ---------------------------------------------------------------------------
# MAO EG IS CURRENT WORK
# ---------------------------------------------------------------------------
def test_mao_eg_is_current_work():
    text = (
        "The Eg of LaNiO3 and MoS2 "
        "are given in Fig. 9b, which "
        "are 2.54 eV and 1.92 eV, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_mao_pair(),
        )
    )

    assert all(
        value.claim_context
        == BandClaimContext.CURRENT_WORK
        for value in values
    )


# ---------------------------------------------------------------------------
# JIANG CB VALUES WITH NHE
# ---------------------------------------------------------------------------
def test_jiang_cb_values_with_nhe():
    pair = (
        PairRecord(
            pair_id="PAIR-0003",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )

    text = (
        "The conduction band potentials "
        "of CaTiO3 and MoS2 are "
        "determined to be -0.19 eV and "
        "-0.42 eV (vs. NHE), "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=pair,
        )
    )

    cb_values = {
        value.formula:
        value
        for value in values
        if value.property_type
        == BandPropertyType.CBM
    }

    assert (
        cb_values[
            "CaTiO3"
        ].numeric_value
        == pytest.approx(
            -0.19
        )
    )

    assert (
        cb_values[
            "MoS2"
        ].numeric_value
        == pytest.approx(
            -0.42
        )
    )

    assert all(
        value.reference_scale
        == BandReferenceScale.NHE
        for value in cb_values.values()
    )


# ---------------------------------------------------------------------------
# VB INHERITS LOCAL NHE CONTEXT
# ---------------------------------------------------------------------------
def test_vb_inherits_local_nhe_context():
    pair = (
        PairRecord(
            pair_id="PAIR-0003",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )

    text = (
        "The conduction band potentials "
        "of CaTiO3 and MoS2 are "
        "determined to be -0.19 eV and "
        "-0.42 eV (vs. NHE), "
        "respectively. Based on the "
        "empirical equation EVB = ECB "
        "+ Eg, the valence band (VB) "
        "potentials of CaTiO3 and MoS2 "
        "are determined to be 3.37 eV "
        "and 1.46 eV, respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=pair,
        )
    )

    vb_values = [
        value
        for value in values
        if value.property_type
        == BandPropertyType.VBM
    ]

    assert len(
        vb_values
    ) == 2

    assert all(
        value.reference_scale
        == BandReferenceScale.NHE
        for value in vb_values
    )


# ---------------------------------------------------------------------------
# QIN LOCAL BAND GAP CONTEXT
# ---------------------------------------------------------------------------
def test_qin_local_band_gap_context():
    text = (
        "The band gap values were "
        "obtained from the optical "
        "analysis. The value is "
        "1.85 eV for MoS2 and "
        "3.07 eV for PbTiO3."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=make_qin_pair(),
        )
    )

    gaps = {
        value.formula:
        value.numeric_value
        for value in values
        if value.property_type
        == BandPropertyType.BAND_GAP
    }

    assert gaps == pytest.approx(
        {
            "MoS2": 1.85,
            "PbTiO3": 3.07,
        }
    )


# ---------------------------------------------------------------------------
# JIANG SIMPLE CB RESPECTIVELY PAIR
# ---------------------------------------------------------------------------
def test_jiang_simple_cb_respectively_pair():
    pair = (
        PairRecord(
            pair_id="PAIR-0003",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )

    text = (
        "The conduction band potentials "
        "of CaTiO3 and MoS2 are "
        "determined to be -0.19 eV "
        "and -0.42 eV versus NHE, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=pair,
        )
    )

    cb_values = {
        value.formula:
        value
        for value in values
        if value.property_type
        == BandPropertyType.CBM
    }

    assert set(
        cb_values
    ) == {
        "CaTiO3",
        "MoS2",
    }

    assert (
        cb_values[
            "CaTiO3"
        ].numeric_value
        == pytest.approx(
            -0.19
        )
    )

    assert (
        cb_values[
            "MoS2"
        ].numeric_value
        == pytest.approx(
            -0.42
        )
    )

    assert all(
        value.reference_scale
        == BandReferenceScale.NHE
        for value in cb_values.values()
    )


# ---------------------------------------------------------------------------
# QIN VB-XPS NUMERIC CLAUSE ORDER
# ---------------------------------------------------------------------------
def test_qin_vb_xps_numeric_clause_order():
    pair = (
        PairRecord(
            pair_id="PAIR-0001",
            psk_formula_reported="PbTiO3",
            psk_formula_normalized="PbTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )

    text = (
        "The highest VB positions of "
        "PbTiO3 and MoS2 were further "
        "evaluated using the VB-XPS "
        "test. As shown in Fig. 6f, "
        "the energy levels of the VB "
        "of MoS2 and PbTiO3 are "
        "0.20 eV and 1.87 eV, "
        "respectively."
    )

    values = (
        extract_structured_band_values(
            text,
            pair=pair,
        )
    )

    vb_values = {
        value.formula:
        value
        for value in values
        if value.property_type
        == BandPropertyType.VBM
    }

    assert set(
        vb_values
    ) == {
        "PbTiO3",
        "MoS2",
    }

    assert (
        vb_values[
            "MoS2"
        ].numeric_value
        == pytest.approx(
            0.20
        )
    )

    assert (
        vb_values[
            "PbTiO3"
        ].numeric_value
        == pytest.approx(
            1.87
        )
    )

    assert all(
        value.claim_context
        == BandClaimContext.CURRENT_WORK
        for value in vb_values.values()
    )

