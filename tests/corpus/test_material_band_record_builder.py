import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
    BandGapType,
    BandReferenceScale,
    MaterialType,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_structured_extraction import (
    StructuredBandValue,
)
from psk_tmd.corpus.material_band_record_builder import (
    build_material_band_record,
    build_pair_material_band_records,
)


# ---------------------------------------------------------------------------
# MAKE PAIR
# ---------------------------------------------------------------------------
def make_pair() -> PairRecord:
    return PairRecord(
        pair_id="PAIR-TEST",
        psk_formula_reported="CaTiO3",
        psk_formula_normalized="CaTiO3",
        tmd_formula_reported="MoS2",
        tmd_formula_normalized="MoS2",
    )


# ---------------------------------------------------------------------------
# MAKE VALUE
# ---------------------------------------------------------------------------
def make_value(
    *,
    property_type: BandPropertyType,
    material_type: MaterialType,
    formula: str,
    numeric_value: float,
    reference_scale: (
        BandReferenceScale | None
    ) = None,
    band_gap_type: (
        BandGapType | None
    ) = None,
    claim_context: BandClaimContext = (
        BandClaimContext.CURRENT_WORK
    ),
    source_text: str = "source text",
) -> StructuredBandValue:
    return StructuredBandValue(
        property_type=property_type,
        material_type=material_type,
        formula=formula,
        numeric_value=numeric_value,
        claim_context=claim_context,
        reference_scale=(
            reference_scale
        ),
        band_gap_type=band_gap_type,
        source_text=source_text,
        extraction_basis="test",
    )


# ---------------------------------------------------------------------------
# BUILD COMPLETE MATERIAL RECORD
# ---------------------------------------------------------------------------
def test_build_complete_material_record():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
            band_gap_type=(
                BandGapType.INDIRECT
            ),
            source_text="Eg source.",
        ),
        make_value(
            property_type=(
                BandPropertyType.CBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=-0.19,
            reference_scale=(
                BandReferenceScale.NHE
            ),
            source_text="CB source.",
        ),
        make_value(
            property_type=(
                BandPropertyType.VBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.37,
            reference_scale=(
                BandReferenceScale.NHE
            ),
            source_text="VB source.",
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-001",
            paper_id="PPR-001",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
            source_location=(
                "Results"
            ),
        )
    )

    assert (
        record.band_record_id
        == "BAND-001"
    )

    assert (
        record.paper_id
        == "PPR-001"
    )

    assert (
        record.pair_id
        == "PAIR-TEST"
    )

    assert (
        record.material_type
        == MaterialType.PSK
    )

    assert (
        record.formula_reported
        == "CaTiO3"
    )

    assert (
        record.reported_band_gap_ev
        == pytest.approx(
            3.56
        )
    )

    assert (
        record.band_gap_type
        == BandGapType.INDIRECT
    )

    assert (
        record.reported_cbm
        == pytest.approx(
            -0.19
        )
    )

    assert (
        record.reported_vbm
        == pytest.approx(
            3.37
        )
    )

    assert (
        record.reported_reference_scale
        == BandReferenceScale.NHE
    )

    assert (
        record.claim_context
        == BandClaimContext.CURRENT_WORK
    )

    assert (
        record.absolute_electronegativity_ev
        is None
    )

    assert (
        record.calculated_cbm_nhe_v
        is None
    )

    assert (
        record.calculated_vbm_nhe_v
        is None
    )


# ---------------------------------------------------------------------------
# UNKNOWN REFERENCE SCALE
# ---------------------------------------------------------------------------
def test_unknown_reference_scale_when_not_reported():
    values = [
        make_value(
            property_type=(
                BandPropertyType.CBM
            ),
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            numeric_value=-1.65,
        ),
        make_value(
            property_type=(
                BandPropertyType.VBM
            ),
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            numeric_value=0.20,
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-002",
            paper_id="PPR-002",
            pair=make_pair(),
            material_type=(
                MaterialType.TMD
            ),
            values=values,
        )
    )

    assert (
        record.reported_reference_scale
        == BandReferenceScale.UNKNOWN
    )


# ---------------------------------------------------------------------------
# MISSING PROPERTY REMAINS NONE
# ---------------------------------------------------------------------------
def test_missing_property_remains_none():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-003",
            paper_id="PPR-003",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
        )
    )

    assert (
        record.reported_band_gap_ev
        == pytest.approx(
            3.56
        )
    )

    assert (
        record.reported_cbm
        is None
    )

    assert (
        record.reported_vbm
        is None
    )


# ---------------------------------------------------------------------------
# CONFLICTING PROPERTY VALUES FAIL
# ---------------------------------------------------------------------------
def test_conflicting_property_values_fail():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
        ),
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.40,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="Conflicting values",
    ):
        build_material_band_record(
            band_record_id="BAND-004",
            paper_id="PPR-004",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
        )


# ---------------------------------------------------------------------------
# MIXED CONTEXT BECOMES AMBIGUOUS
# ---------------------------------------------------------------------------
def test_mixed_context_becomes_ambiguous():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
            claim_context=(
                BandClaimContext.CURRENT_WORK
            ),
        ),
        make_value(
            property_type=(
                BandPropertyType.CBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=-0.19,
            claim_context=(
                BandClaimContext.AMBIGUOUS
            ),
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-005",
            paper_id="PPR-005",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
        )
    )

    assert (
        record.claim_context
        == BandClaimContext.AMBIGUOUS
    )


# ---------------------------------------------------------------------------
# CONFLICTING REFERENCE SCALE BECOMES UNKNOWN
# ---------------------------------------------------------------------------
def test_conflicting_reference_scale_becomes_unknown():
    values = [
        make_value(
            property_type=(
                BandPropertyType.CBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=-0.19,
            reference_scale=(
                BandReferenceScale.NHE
            ),
        ),
        make_value(
            property_type=(
                BandPropertyType.VBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.37,
            reference_scale=(
                BandReferenceScale.AG_AGCL
            ),
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-006",
            paper_id="PPR-006",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
        )
    )

    assert (
        record.reported_reference_scale
        == BandReferenceScale.UNKNOWN
    )


# ---------------------------------------------------------------------------
# SOURCE TEXT PRESERVES DISTINCT CLAIMS
# ---------------------------------------------------------------------------
def test_source_text_preserves_distinct_claims():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
            source_text="Band-gap passage.",
        ),
        make_value(
            property_type=(
                BandPropertyType.CBM
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=-0.19,
            source_text="Band-edge passage.",
        ),
    ]

    record = (
        build_material_band_record(
            band_record_id="BAND-007",
            paper_id="PPR-007",
            pair=make_pair(),
            material_type=(
                MaterialType.PSK
            ),
            values=values,
        )
    )

    assert (
        "Band-gap passage."
        in record.source_text
    )

    assert (
        "Band-edge passage."
        in record.source_text
    )


# ---------------------------------------------------------------------------
# BUILD TWO RECORDS FOR PAIR
# ---------------------------------------------------------------------------
def test_build_pair_material_band_records():
    values = [
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            numeric_value=3.56,
        ),
        make_value(
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            numeric_value=1.88,
        ),
    ]

    records = (
        build_pair_material_band_records(
            paper_id="PPR-008",
            pair=make_pair(),
            values=values,
            psk_band_record_id=(
                "BAND-PSK"
            ),
            tmd_band_record_id=(
                "BAND-TMD"
            ),
        )
    )

    assert len(
        records
    ) == 2

    assert (
        records[
            0
        ].material_type
        == MaterialType.PSK
    )

    assert (
        records[
            1
        ].material_type
        == MaterialType.TMD
    )

    assert (
        records[
            0
        ].reported_band_gap_ev
        == pytest.approx(
            3.56
        )
    )

    assert (
        records[
            1
        ].reported_band_gap_ev
        == pytest.approx(
            1.88
        )
    )


