from psk_tmd.common.models import (
    MaterialBandRecord,
    PairBandAlignmentRecord,
)


# ---------------------------------------------------------------------------
# VALIDATE BAND RECORD PAIR
# ---------------------------------------------------------------------------
def validate_band_record_pair(
    oxidation_record: MaterialBandRecord,
    reduction_record: MaterialBandRecord,
) -> None:
    if (
        oxidation_record.pair_id
        != reduction_record.pair_id
    ):
        raise ValueError(
            "Oxidation and reduction band "
            "records must belong to the "
            "same pair."
        )

    if (
        oxidation_record.band_record_id
        == reduction_record.band_record_id
    ):
        raise ValueError(
            "Oxidation and reduction band "
            "records must be different."
        )


# ---------------------------------------------------------------------------
# CALCULATE MEDIATED BAND DIFFERENCE
# ---------------------------------------------------------------------------
def calculate_mediated_band_difference(
    *,
    oxidation_cbm_nhe_v: float,
    reduction_vbm_nhe_v: float,
) -> float:
    return (
        oxidation_cbm_nhe_v
        - reduction_vbm_nhe_v
    )


# ---------------------------------------------------------------------------
# BUILD PAIR BAND ALIGNMENT
# ---------------------------------------------------------------------------
def build_pair_band_alignment(
    *,
    band_alignment_id: str,
    oxidation_record: MaterialBandRecord,
    reduction_record: MaterialBandRecord,
    role_assignment_basis: str,
) -> PairBandAlignmentRecord:
    validate_band_record_pair(
        oxidation_record=oxidation_record,
        reduction_record=reduction_record,
    )

    if not band_alignment_id.strip():
        raise ValueError(
            "Band alignment ID must not "
            "be empty."
        )

    if not role_assignment_basis.strip():
        raise ValueError(
            "Role assignment basis must "
            "not be empty."
        )

    oxidation_cbm_nhe_v = (
        oxidation_record
        .calculated_cbm_nhe_v
    )

    reduction_vbm_nhe_v = (
        reduction_record
        .calculated_vbm_nhe_v
    )

    if (
        oxidation_cbm_nhe_v
        is None
    ):
        raise ValueError(
            "Oxidation material must have "
            "a standardized calculated CBM."
        )

    if (
        reduction_vbm_nhe_v
        is None
    ):
        raise ValueError(
            "Reduction material must have "
            "a standardized calculated VBM."
        )

    mediated_band_difference_nhe_v = (
        calculate_mediated_band_difference(
            oxidation_cbm_nhe_v=(
                oxidation_cbm_nhe_v
            ),
            reduction_vbm_nhe_v=(
                reduction_vbm_nhe_v
            ),
        )
    )

    return (
        PairBandAlignmentRecord(
            band_alignment_id=(
                band_alignment_id
            ),
            pair_id=(
                oxidation_record.pair_id
            ),
            oxidation_band_record_id=(
                oxidation_record
                .band_record_id
            ),
            reduction_band_record_id=(
                reduction_record
                .band_record_id
            ),
            oxidation_material_type=(
                oxidation_record
                .material_type
            ),
            reduction_material_type=(
                reduction_record
                .material_type
            ),
            oxidation_formula=(
                oxidation_record
                .formula_normalized
                or oxidation_record
                .formula_reported
            ),
            reduction_formula=(
                reduction_record
                .formula_normalized
                or reduction_record
                .formula_reported
            ),
            oxidation_cbm_nhe_v=(
                oxidation_cbm_nhe_v
            ),
            reduction_vbm_nhe_v=(
                reduction_vbm_nhe_v
            ),
            mediated_band_difference_nhe_v=(
                mediated_band_difference_nhe_v
            ),
            role_assignment_basis=(
                role_assignment_basis
            ),
        )
    )

