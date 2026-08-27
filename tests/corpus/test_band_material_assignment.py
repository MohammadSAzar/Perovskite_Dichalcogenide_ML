from psk_tmd.common.constants import (
    BandClaimContext,
    MaterialType,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_claims import (
    BandClaimCandidate,
)
from psk_tmd.corpus.band_material_assignment import (
    assign_band_claim_to_material,
    assign_band_claims_to_materials,
    formula_occurs_in_text,
    normalize_formula_text,
)


# ---------------------------------------------------------------------------
# BUILD PAIR
# ---------------------------------------------------------------------------
def make_pair() -> PairRecord:
    return (
        PairRecord(
            pair_id="PAIR-0001",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        )
    )


# ---------------------------------------------------------------------------
# BUILD CLAIM
# ---------------------------------------------------------------------------
def make_claim(
    source_text: str,
) -> BandClaimCandidate:
    return (
        BandClaimCandidate(
            property_type=(
                BandPropertyType
                .BAND_GAP
            ),
            numeric_value=2.40,
            matched_text=(
                "band gap of 2.40 eV"
            ),
            source_text=(
                source_text
            ),
            start=0,
            end=19,
            claim_context=(
                BandClaimContext
                .CURRENT_WORK
            ),
        )
    )


# ---------------------------------------------------------------------------
# NORMALIZE UNICODE SUBSCRIPTS
# ---------------------------------------------------------------------------
def test_normalize_unicode_subscripts():
    result = (
        normalize_formula_text(
            "MoS₂"
        )
    )

    assert result == "MoS2"


# ---------------------------------------------------------------------------
# FORMULA OCCURS
# ---------------------------------------------------------------------------
def test_formula_occurs_in_text():
    assert formula_occurs_in_text(
        "The CaTiO3 band gap was measured.",
        "CaTiO3",
    )


# ---------------------------------------------------------------------------
# FORMULA WITH UNICODE SUBSCRIPT OCCURS
# ---------------------------------------------------------------------------
def test_unicode_formula_occurs_in_text():
    assert formula_occurs_in_text(
        "The MoS₂ band gap was measured.",
        "MoS2",
    )


# ---------------------------------------------------------------------------
# ASSIGN PSK CLAIM
# ---------------------------------------------------------------------------
def test_assign_psk_claim():
    claim = make_claim(
        "The CaTiO3 band gap "
        "was measured as 2.40 eV."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=make_pair(),
        )
    )

    assert (
        result.material_type
        == MaterialType.PSK
    )

    assert (
        result.formula
        == "CaTiO3"
    )


# ---------------------------------------------------------------------------
# ASSIGN TMD CLAIM
# ---------------------------------------------------------------------------
def test_assign_tmd_claim():
    claim = make_claim(
        "The MoS2 band gap "
        "was measured as 2.40 eV."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=make_pair(),
        )
    )

    assert (
        result.material_type
        == MaterialType.TMD
    )

    assert (
        result.formula
        == "MoS2"
    )


# ---------------------------------------------------------------------------
# BOTH MATERIALS REMAIN UNRESOLVED
# ---------------------------------------------------------------------------
def test_both_materials_remain_unresolved():
    claim = make_claim(
        "The CaTiO3/MoS2 system "
        "was analyzed."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=make_pair(),
        )
    )

    assert (
        result.material_type
        is None
    )

    assert (
        result.formula
        is None
    )


# ---------------------------------------------------------------------------
# NO MATERIAL REMAINS UNRESOLVED
# ---------------------------------------------------------------------------
def test_no_material_remains_unresolved():
    claim = make_claim(
        "The band gap was "
        "measured as 2.40 eV."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=make_pair(),
        )
    )

    assert (
        result.material_type
        is None
    )

    assert (
        result.formula
        is None
    )


# ---------------------------------------------------------------------------
# DOPED PSK IS PRESERVED
# ---------------------------------------------------------------------------
def test_doped_psk_is_preserved():
    pair = (
        PairRecord(
            pair_id="PAIR-0002",
            psk_formula_reported=(
                "La0.8Sr0.2FeO2.8N0.2"
            ),
            psk_formula_normalized=(
                "La0.8Sr0.2FeO2.8N0.2"
            ),
            tmd_formula_reported="WS2",
            tmd_formula_normalized="WS2",
        )
    )

    claim = make_claim(
        "The La0.8Sr0.2FeO2.8N0.2 "
        "band gap was 2.1 eV."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=pair,
        )
    )

    assert (
        result.material_type
        == MaterialType.PSK
    )

    assert (
        result.formula
        == "La0.8Sr0.2FeO2.8N0.2"
    )


# ---------------------------------------------------------------------------
# DOPED TMD IS PRESERVED
# ---------------------------------------------------------------------------
def test_doped_tmd_is_preserved():
    pair = (
        PairRecord(
            pair_id="PAIR-0003",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported=(
                "MoS1.5Se0.5"
            ),
            tmd_formula_normalized=(
                "MoS1.5Se0.5"
            ),
        )
    )

    claim = make_claim(
        "MoS1.5Se0.5 showed a "
        "band gap of 1.8 eV."
    )

    result = (
        assign_band_claim_to_material(
            claim,
            pair=pair,
        )
    )

    assert (
        result.material_type
        == MaterialType.TMD
    )

    assert (
        result.formula
        == "MoS1.5Se0.5"
    )


# ---------------------------------------------------------------------------
# ASSIGN MULTIPLE CLAIMS
# ---------------------------------------------------------------------------
def test_assign_multiple_claims():
    claims = [
        make_claim(
            "CaTiO3 has a band gap "
            "of 3.2 eV."
        ),
        make_claim(
            "MoS2 has a band gap "
            "of 1.8 eV."
        ),
    ]

    results = (
        assign_band_claims_to_materials(
            claims,
            pair=make_pair(),
        )
    )

    assert [
        result.material_type
        for result in results
    ] == [
        MaterialType.PSK,
        MaterialType.TMD,
    ]

