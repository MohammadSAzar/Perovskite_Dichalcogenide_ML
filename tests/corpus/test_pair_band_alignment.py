import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
    MaterialType,
    ChargeTransferClass,
)
from psk_tmd.common.models import (
    MaterialBandRecord,
)
from psk_tmd.corpus.pair_band_alignment import (
    validate_band_record_pair,
    build_pair_band_alignment,
    calculate_mediated_band_difference,
    is_band_offset_eligible,
    validate_band_offset_eligibility,
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
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
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        )


# ---------------------------------------------------------------------------
# TYPE-II IS BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_type_ii_is_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass.TYPE_II
        )
        is True
    )


# ---------------------------------------------------------------------------
# MEDIATED RECOMBINATION IS BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_mediated_recombination_is_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
        is True
    )


# ---------------------------------------------------------------------------
# TYPE-I IS NOT BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_type_i_is_not_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass.TYPE_I
        )
        is False
    )


# ---------------------------------------------------------------------------
# TYPE-III IS NOT BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_type_iii_is_not_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass.TYPE_III
        )
        is False
    )


# ---------------------------------------------------------------------------
# PN IS NOT BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_pn_is_not_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass.PN
        )
        is False
    )


# ---------------------------------------------------------------------------
# SCHOTTKY IS NOT BAND OFFSET ELIGIBLE
# ---------------------------------------------------------------------------
def test_schottky_is_not_band_offset_eligible():
    assert (
        is_band_offset_eligible(
            ChargeTransferClass.SCHOTTKY
        )
        is False
    )


# ---------------------------------------------------------------------------
# INVALID BAND OFFSET CLASS FAILS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "charge_transfer_class",
    [
        ChargeTransferClass.TYPE_I,
        ChargeTransferClass.TYPE_III,
        ChargeTransferClass.PN,
        ChargeTransferClass.SCHOTTKY,
    ],
)
def test_invalid_band_offset_class_fails(
    charge_transfer_class,
):
    with pytest.raises(
        ValueError,
        match=(
            "Band offset is defined only"
        ),
    ):
        validate_band_offset_eligibility(
            charge_transfer_class
        )


# ---------------------------------------------------------------------------
# MAKE STANDARDIZED BAND RECORD
# ---------------------------------------------------------------------------
def make_standardized_band_record(
    *,
    band_record_id: str,
    pair_id: str,
    material_type: MaterialType,
    formula: str,
    cbm: float,
    vbm: float,
) -> MaterialBandRecord:
    return MaterialBandRecord(
        band_record_id=band_record_id,
        paper_id="PPR-TEST",
        pair_id=pair_id,
        material_type=material_type,
        formula_reported=formula,
        formula_normalized=formula,
        reported_band_gap_ev=None,
        calculated_cbm_nhe_v=cbm,
        calculated_vbm_nhe_v=vbm,
    )


# ---------------------------------------------------------------------------
# TYPE-II BAND ALIGNMENT BUILDS
# ---------------------------------------------------------------------------
def test_type_ii_band_alignment_builds():
    oxidation_record = (
        make_standardized_band_record(
            band_record_id="BAND-OP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            cbm=-0.89,
            vbm=2.67,
        )
    )

    reduction_record = (
        make_standardized_band_record(
            band_record_id="BAND-RP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            cbm=-0.11,
            vbm=1.77,
        )
    )

    alignment = (
        build_pair_band_alignment(
            band_alignment_id=(
                "ALIGN-001"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_II
            ),
            role_assignment_basis=(
                "Explicit Type-II "
                "charge-transfer assignment."
            ),
        )
    )

    assert (
        alignment
        .mediated_band_difference_nhe_v
        == pytest.approx(
            -2.66
        )
    )


# ---------------------------------------------------------------------------
# MEDIATED BAND ALIGNMENT BUILDS
# ---------------------------------------------------------------------------
def test_mediated_band_alignment_builds():
    oxidation_record = (
        make_standardized_band_record(
            band_record_id="BAND-OP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.PSK
            ),
            formula="CaTiO3",
            cbm=-0.89,
            vbm=2.67,
        )
    )

    reduction_record = (
        make_standardized_band_record(
            band_record_id="BAND-RP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            cbm=-0.11,
            vbm=1.77,
        )
    )

    alignment = (
        build_pair_band_alignment(
            band_alignment_id=(
                "ALIGN-002"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
            role_assignment_basis=(
                "Curated Z-scheme "
                "charge-transfer assignment."
            ),
        )
    )

    assert (
        alignment
        .mediated_band_difference_nhe_v
        == pytest.approx(
            -2.66
        )
    )


# ---------------------------------------------------------------------------
# TYPE-I BAND ALIGNMENT IS REJECTED
# ---------------------------------------------------------------------------
def test_type_i_band_alignment_is_rejected():
    oxidation_record = (
        make_standardized_band_record(
            band_record_id="BAND-OP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.PSK
            ),
            formula="LaNiO3",
            cbm=-0.13,
            vbm=2.41,
        )
    )

    reduction_record = (
        make_standardized_band_record(
            band_record_id="BAND-RP",
            pair_id="PAIR-TEST",
            material_type=(
                MaterialType.TMD
            ),
            formula="MoS2",
            cbm=-0.13,
            vbm=1.79,
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "Band offset is defined only"
        ),
    ):
        build_pair_band_alignment(
            band_alignment_id=(
                "ALIGN-003"
            ),
            oxidation_record=(
                oxidation_record
            ),
            reduction_record=(
                reduction_record
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_I
            ),
            role_assignment_basis=(
                "Type-I test."
            ),
        )


