from psk_tmd.common.constants import (
    BandClaimContext,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
    MaterialBandRecord,
)
from psk_tmd.corpus.band_calculation import (
    calculate_standard_band_edges,
)
from psk_tmd.corpus.compound_electronegativity import (
    calculate_compound_absolute_electronegativity,
)


# ---------------------------------------------------------------------------
# CLEAR STANDARDIZED BAND CALCULATION
# ---------------------------------------------------------------------------
def clear_standardized_band_calculation(
    record: MaterialBandRecord,
) -> MaterialBandRecord:
    return record.model_copy(
        update={
            "absolute_electronegativity_ev": None,
            "calculated_cbm_nhe_v": None,
            "calculated_vbm_nhe_v": None,
        }
    )


# ---------------------------------------------------------------------------
# POPULATE MATERIAL ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def populate_material_electronegativity(
    record: MaterialBandRecord,
    *,
    composition: dict[
        str,
        float,
    ],
    elemental_lookup: dict[
        str,
        ElementElectronegativityRecord,
    ],
) -> MaterialBandRecord:
    absolute_electronegativity_ev = (
        calculate_compound_absolute_electronegativity(
            composition=composition,
            elemental_lookup=elemental_lookup,
        )
    )

    return record.model_copy(
        update={
            "absolute_electronegativity_ev": (
                absolute_electronegativity_ev
            ),
        }
    )


# ---------------------------------------------------------------------------
# POPULATE CALCULATED BAND EDGES
# ---------------------------------------------------------------------------
def populate_calculated_band_edges(
    record: MaterialBandRecord,
) -> MaterialBandRecord:
    if (
        record.claim_context
        != BandClaimContext.CURRENT_WORK
    ):
        return record.model_copy(
            update={
                "calculated_cbm_nhe_v": None,
                "calculated_vbm_nhe_v": None,
            }
        )

    if (
        record.reported_band_gap_ev
        is None
        or record.absolute_electronegativity_ev
        is None
    ):
        return record.model_copy(
            update={
                "calculated_cbm_nhe_v": None,
                "calculated_vbm_nhe_v": None,
            }
        )

    (
        calculated_cbm_nhe_v,
        calculated_vbm_nhe_v,
    ) = calculate_standard_band_edges(
        absolute_electronegativity_ev=(
            record.absolute_electronegativity_ev
        ),
        band_gap_ev=(
            record.reported_band_gap_ev
        ),
    )

    return record.model_copy(
        update={
            "calculated_cbm_nhe_v": (
                calculated_cbm_nhe_v
            ),
            "calculated_vbm_nhe_v": (
                calculated_vbm_nhe_v
            ),
        }
    )


# ---------------------------------------------------------------------------
# STANDARDIZE MATERIAL BAND RECORD
# ---------------------------------------------------------------------------
def standardize_material_band_record(
    record: MaterialBandRecord,
    *,
    composition: dict[
        str,
        float,
    ],
    elemental_lookup: dict[
        str,
        ElementElectronegativityRecord,
    ],
) -> MaterialBandRecord:
    if (
        record.claim_context
        != BandClaimContext.CURRENT_WORK
    ):
        return (
            clear_standardized_band_calculation(
                record
            )
        )

    with_electronegativity = (
        populate_material_electronegativity(
            record,
            composition=composition,
            elemental_lookup=elemental_lookup,
        )
    )

    return populate_calculated_band_edges(
        with_electronegativity
    )

