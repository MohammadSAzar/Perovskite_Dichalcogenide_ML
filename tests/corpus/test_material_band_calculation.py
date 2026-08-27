import pytest

from psk_tmd.common.constants import (
    BandClaimContext,
    ElectronegativityValueStatus,
    MaterialType,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
    MaterialBandRecord,
)
from psk_tmd.corpus.material_band_calculation import (
    clear_standardized_band_calculation,
    populate_calculated_band_edges,
    populate_material_electronegativity,
    standardize_material_band_record,
)


# ---------------------------------------------------------------------------
# BUILD TEST BAND RECORD
# ---------------------------------------------------------------------------
def make_band_record(
    *,
    band_gap_ev: float | None,
    electronegativity_ev: float | None = None,
    claim_context: BandClaimContext = (
        BandClaimContext.CURRENT_WORK
    ),
) -> MaterialBandRecord:
    return (
        MaterialBandRecord(
            band_record_id="BAND-0001",
            paper_id="PPR-0001",
            pair_id="PAIR-0001",
            material_type=(
                MaterialType.PSK
            ),
            formula_reported="CaTiO3",
            formula_normalized="CaTiO3",
            reported_band_gap_ev=(
                band_gap_ev
            ),
            absolute_electronegativity_ev=(
                electronegativity_ev
            ),
            claim_context=(
                claim_context
            ),
        )
    )


# ---------------------------------------------------------------------------
# BUILD TEST ELEMENT RECORD
# ---------------------------------------------------------------------------
def make_element_record(
    symbol: str,
    value: float,
) -> ElementElectronegativityRecord:
    return (
        ElementElectronegativityRecord(
            element_symbol=symbol,
            chemical_potential_ev=(
                -value
            ),
            absolute_electronegativity_ev=(
                value
            ),
            value_status=(
                ElectronegativityValueStatus
                .TABULATED
            ),
        )
    )


# ---------------------------------------------------------------------------
# POPULATE MATERIAL ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def test_populate_material_electronegativity():
    record = make_band_record(
        band_gap_ev=3.2,
    )

    lookup = {
        "Ca": make_element_record(
            "Ca",
            3.07,
        ),
        "Ti": make_element_record(
            "Ti",
            3.45,
        ),
        "O": make_element_record(
            "O",
            7.54,
        ),
    }

    result = (
        populate_material_electronegativity(
            record,
            composition={
                "Ca": 1.0,
                "Ti": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        3.07
        * 3.45
        * 7.54**3
    ) ** (
        1.0 / 5.0
    )

    assert (
        result.absolute_electronegativity_ev
        == pytest.approx(
            expected
        )
    )


# ---------------------------------------------------------------------------
# POPULATE CALCULATED BAND EDGES
# ---------------------------------------------------------------------------
def test_populate_calculated_band_edges():
    record = make_band_record(
        band_gap_ev=3.2,
        electronegativity_ev=5.3878,
    )

    result = (
        populate_calculated_band_edges(
            record
        )
    )

    expected_cbm = (
        5.3878
        - 4.5
        - 3.2 / 2.0
    )

    expected_vbm = (
        5.3878
        - 4.5
        + 3.2 / 2.0
    )

    assert (
        result.calculated_cbm_nhe_v
        == pytest.approx(
            expected_cbm
        )
    )

    assert (
        result.calculated_vbm_nhe_v
        == pytest.approx(
            expected_vbm
        )
    )


# ---------------------------------------------------------------------------
# MISSING BAND GAP LEAVES BAND EDGES EMPTY
# ---------------------------------------------------------------------------
def test_missing_band_gap_leaves_band_edges_empty():
    record = make_band_record(
        band_gap_ev=None,
        electronegativity_ev=5.3878,
    )

    result = (
        populate_calculated_band_edges(
            record
        )
    )

    assert (
        result.calculated_cbm_nhe_v
        is None
    )

    assert (
        result.calculated_vbm_nhe_v
        is None
    )


# ---------------------------------------------------------------------------
# PRIOR LITERATURE DOES NOT GET STANDARDIZED BAND EDGES
# ---------------------------------------------------------------------------
def test_prior_literature_does_not_get_standardized_band_edges():
    record = make_band_record(
        band_gap_ev=3.2,
        electronegativity_ev=5.3878,
        claim_context=(
            BandClaimContext
            .PRIOR_LITERATURE
        ),
    )

    result = (
        populate_calculated_band_edges(
            record
        )
    )

    assert (
        result.calculated_cbm_nhe_v
        is None
    )

    assert (
        result.calculated_vbm_nhe_v
        is None
    )


# ---------------------------------------------------------------------------
# FULL STANDARDIZATION
# ---------------------------------------------------------------------------
def test_standardize_material_band_record():
    record = make_band_record(
        band_gap_ev=3.2,
    )

    lookup = {
        "Ca": make_element_record(
            "Ca",
            3.07,
        ),
        "Ti": make_element_record(
            "Ti",
            3.45,
        ),
        "O": make_element_record(
            "O",
            7.54,
        ),
    }

    result = (
        standardize_material_band_record(
            record,
            composition={
                "Ca": 1.0,
                "Ti": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected_chi = (
        3.07
        * 3.45
        * 7.54**3
    ) ** (
        1.0 / 5.0
    )

    expected_cbm = (
        expected_chi
        - 4.5
        - 3.2 / 2.0
    )

    expected_vbm = (
        expected_chi
        - 4.5
        + 3.2 / 2.0
    )

    assert (
        result.absolute_electronegativity_ev
        == pytest.approx(
            expected_chi
        )
    )

    assert (
        result.calculated_cbm_nhe_v
        == pytest.approx(
            expected_cbm
        )
    )

    assert (
        result.calculated_vbm_nhe_v
        == pytest.approx(
            expected_vbm
        )
    )


# ---------------------------------------------------------------------------
# FULL STANDARDIZATION SUPPORTS DOPED COMPOSITION
# ---------------------------------------------------------------------------
def test_standardization_supports_doped_composition():
    record = make_band_record(
        band_gap_ev=2.4,
    )

    lookup = {
        "La": make_element_record(
            "La",
            3.03,
        ),
        "Sr": make_element_record(
            "Sr",
            2.88,
        ),
        "Fe": make_element_record(
            "Fe",
            4.03,
        ),
        "O": make_element_record(
            "O",
            7.54,
        ),
        "N": make_element_record(
            "N",
            7.27,
        ),
    }

    composition = {
        "La": 0.8,
        "Sr": 0.2,
        "Fe": 1.0,
        "O": 2.8,
        "N": 0.2,
    }

    result = (
        standardize_material_band_record(
            record,
            composition=composition,
            elemental_lookup=lookup,
        )
    )

    expected_chi = (
        3.03**0.8
        * 2.88**0.2
        * 4.03
        * 7.54**2.8
        * 7.27**0.2
    ) ** (
        1.0 / 5.0
    )

    assert (
        result.absolute_electronegativity_ev
        == pytest.approx(
            expected_chi
        )
    )

    assert (
        result.calculated_vbm_nhe_v
        - result.calculated_cbm_nhe_v
        == pytest.approx(
            2.4
        )
    )


# ---------------------------------------------------------------------------
# PRIOR LITERATURE FULL STANDARDIZATION IS CLEARED
# ---------------------------------------------------------------------------
def test_prior_literature_full_standardization_is_cleared():
    record = make_band_record(
        band_gap_ev=3.2,
        electronegativity_ev=5.0,
        claim_context=(
            BandClaimContext
            .PRIOR_LITERATURE
        ),
    )

    record = record.model_copy(
        update={
            "calculated_cbm_nhe_v": -1.0,
            "calculated_vbm_nhe_v": 2.2,
        }
    )

    result = (
        standardize_material_band_record(
            record,
            composition={
                "Ca": 1.0,
                "Ti": 1.0,
                "O": 3.0,
            },
            elemental_lookup={},
        )
    )

    assert (
        result.absolute_electronegativity_ev
        is None
    )

    assert (
        result.calculated_cbm_nhe_v
        is None
    )

    assert (
        result.calculated_vbm_nhe_v
        is None
    )


# ---------------------------------------------------------------------------
# CLEAR STANDARDIZED CALCULATION
# ---------------------------------------------------------------------------
def test_clear_standardized_band_calculation():
    record = make_band_record(
        band_gap_ev=3.2,
        electronegativity_ev=5.0,
    )

    record = record.model_copy(
        update={
            "calculated_cbm_nhe_v": -1.1,
            "calculated_vbm_nhe_v": 2.1,
        }
    )

    result = (
        clear_standardized_band_calculation(
            record
        )
    )

    assert (
        result.absolute_electronegativity_ev
        is None
    )

    assert (
        result.calculated_cbm_nhe_v
        is None
    )

    assert (
        result.calculated_vbm_nhe_v
        is None
    )


# ---------------------------------------------------------------------------
# ORIGINAL RECORD IS NOT MUTATED
# ---------------------------------------------------------------------------
def test_original_record_is_not_mutated():
    record = make_band_record(
        band_gap_ev=3.2,
        electronegativity_ev=5.3878,
    )

    result = (
        populate_calculated_band_edges(
            record
        )
    )

    assert (
        record.calculated_cbm_nhe_v
        is None
    )

    assert (
        record.calculated_vbm_nhe_v
        is None
    )

    assert result is not record


