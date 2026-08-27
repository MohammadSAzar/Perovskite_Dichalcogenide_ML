import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
    MaterialType,
)
from psk_tmd.common.models import (
    MaterialBandRecord,
)
from psk_tmd.corpus.pair_band_alignment import (
    build_pair_band_alignment,
    calculate_mediated_band_difference,
    validate_band_record_pair,
)


# ---------------------------------------------------------------------------
# BUILD TEST BAND RECORD
# ---------------------------------------------------------------------------
def make_band_record(
    *,
    band_record_id: str,
    pair_id: str,
    material_type: MaterialType,
    formula: str,
    calculated_cbm_nhe_v: float | None,
    calculated_vbm_nhe_v: float | None,
) -> MaterialBandRecord:
    return (
        MaterialBandRecord(
            band_record_id=(
                band_record_id
            ),
            paper_id="PPR-0001",
            pair_id=pair_id,
            material_type=material_type,
            formula_reported=formula,
            formula_normalized=formula,
            calculated_cbm_nhe_v=(
                calculated_cbm_nhe_v
            ),
            calculated_vbm_nhe_v=(
                calculated_vbm_nhe_v
            ),
            claim_context=(
                BandClaimContext
                .CURRENT_WORK
            ),
        )
    )


# ---------------------------------------------------------------------------
# MEDIATED BAND DIFFERENCE
# ---------------------------------------------------------------------------
def test_mediated_band_difference():
    result = (
        calculate_mediated_band_difference(
            oxidation_cbm_nhe_v=-0.60,
            reduction_vbm_nhe_v=2.10,
        )
    )

    assert result == pytest.approx(
        -2.70
    )


# ---------------------------------------------------------------------------
# SIGN IS PRESERVED
# ---------------------------------------------------------------------------
def test_mediated_band_difference_preserves_sign():
    result = (
        calculate_mediated_band_difference(
            oxidation_cbm_nhe_v=1.20,
            reduction_vbm_nhe_v=0.50,
        )
    )

    assert result == pytest.approx(
        0.70
    )


# ---------------------------------------------------------------------------
# BUILD PAIR BAND ALIGNMENT
# ---------------------------------------------------------------------------
def test_build_pair_band_alignment():
    oxidation_record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    reduction_record = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=1.10,
        )
    )

    result = (
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0001"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            role_assignment_basis=(
                "Manual mechanism "
                "interpretation."
            ),
        )
    )

    assert (
        result.pair_id
        == "PAIR-0001"
    )

    assert (
        result.oxidation_formula
        == "CaTiO3"
    )

    assert (
        result.reduction_formula
        == "MoS2"
    )

    assert (
        result.oxidation_cbm_nhe_v
        == pytest.approx(
            -0.70
        )
    )

    assert (
        result.reduction_vbm_nhe_v
        == pytest.approx(
            1.10
        )
    )

    assert (
        result.mediated_band_difference_nhe_v
        == pytest.approx(
            -1.80
        )
    )


# ---------------------------------------------------------------------------
# ROLE ASSIGNMENT IS EXPLICIT
# ---------------------------------------------------------------------------
def test_reversing_roles_changes_result():
    first = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    second = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=1.10,
        )
    )

    forward = (
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0001"
            ),
            oxidation_record=first,
            reduction_record=second,
            role_assignment_basis=(
                "Test forward roles."
            ),
        )
    )

    reversed_alignment = (
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0002"
            ),
            oxidation_record=second,
            reduction_record=first,
            role_assignment_basis=(
                "Test reversed roles."
            ),
        )
    )

    assert (
        forward
        .mediated_band_difference_nhe_v
        == pytest.approx(
            -1.80
        )
    )

    assert (
        reversed_alignment
        .mediated_band_difference_nhe_v
        == pytest.approx(
            -3.30
        )
    )


# ---------------------------------------------------------------------------
# DIFFERENT PAIRS FAIL
# ---------------------------------------------------------------------------
def test_different_pairs_fail():
    oxidation_record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    reduction_record = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0002",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=1.10,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "same pair"
        ),
    ):
        validate_band_record_pair(
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
        )


# ---------------------------------------------------------------------------
# SAME BAND RECORD FAILS
# ---------------------------------------------------------------------------
def test_same_band_record_fails():
    record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "must be different"
        ),
    ):
        validate_band_record_pair(
            oxidation_record=record,
            reduction_record=record,
        )


# ---------------------------------------------------------------------------
# MISSING OXIDATION CBM FAILS
# ---------------------------------------------------------------------------
def test_missing_oxidation_cbm_fails():
    oxidation_record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=None,
            calculated_vbm_nhe_v=2.50,
        )
    )

    reduction_record = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=1.10,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "standardized calculated CBM"
        ),
    ):
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0001"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            role_assignment_basis=(
                "Manual assignment."
            ),
        )


# ---------------------------------------------------------------------------
# MISSING REDUCTION VBM FAILS
# ---------------------------------------------------------------------------
def test_missing_reduction_vbm_fails():
    oxidation_record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    reduction_record = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=None,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "standardized calculated VBM"
        ),
    ):
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0001"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            role_assignment_basis=(
                "Manual assignment."
            ),
        )


# ---------------------------------------------------------------------------
# EMPTY ROLE BASIS FAILS
# ---------------------------------------------------------------------------
def test_empty_role_basis_fails():
    oxidation_record = (
        make_band_record(
            band_record_id="BAND-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            calculated_cbm_nhe_v=-0.70,
            calculated_vbm_nhe_v=2.50,
        )
    )

    reduction_record = (
        make_band_record(
            band_record_id="BAND-0002",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            calculated_cbm_nhe_v=-0.80,
            calculated_vbm_nhe_v=1.10,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Role assignment basis"
        ),
    ):
        build_pair_band_alignment(
            band_alignment_id=(
                "BALIGN-0001"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            role_assignment_basis="",
        )

