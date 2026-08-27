import pytest

from psk_tmd.corpus.band_calculation import (
    FREE_ELECTRON_ENERGY_EV,
    calculate_standard_band_edges,
    validate_band_edge_gap,
)


# ---------------------------------------------------------------------------
# DEFAULT FREE-ELECTRON ENERGY
# ---------------------------------------------------------------------------
def test_default_free_electron_energy():
    assert (
        FREE_ELECTRON_ENERGY_EV
        == pytest.approx(
            4.5
        )
    )


# ---------------------------------------------------------------------------
# CALCULATE STANDARD BAND EDGES
# ---------------------------------------------------------------------------
def test_calculate_standard_band_edges():
    cbm, vbm = (
        calculate_standard_band_edges(
            absolute_electronegativity_ev=(
                5.8
            ),
            band_gap_ev=2.5,
        )
    )

    assert cbm == pytest.approx(
        0.05
    )

    assert vbm == pytest.approx(
        2.55
    )


# ---------------------------------------------------------------------------
# BAND EDGE DIFFERENCE EQUALS BAND GAP
# ---------------------------------------------------------------------------
def test_band_edge_difference_equals_band_gap():
    cbm, vbm = (
        calculate_standard_band_edges(
            absolute_electronegativity_ev=(
                5.3878
            ),
            band_gap_ev=3.2,
        )
    )

    assert (
        vbm
        - cbm
    ) == pytest.approx(
        3.2
    )


# ---------------------------------------------------------------------------
# VALIDATE BAND EDGE GAP
# ---------------------------------------------------------------------------
def test_validate_band_edge_gap():
    validate_band_edge_gap(
        cbm_nhe_v=0.05,
        vbm_nhe_v=2.55,
        band_gap_ev=2.5,
    )


# ---------------------------------------------------------------------------
# INVALID BAND EDGE GAP FAILS
# ---------------------------------------------------------------------------
def test_invalid_band_edge_gap_fails():
    with pytest.raises(
        ValueError,
        match=(
            "does not match"
        ),
    ):
        validate_band_edge_gap(
            cbm_nhe_v=0.0,
            vbm_nhe_v=2.0,
            band_gap_ev=2.5,
        )


# ---------------------------------------------------------------------------
# NEGATIVE BAND GAP FAILS
# ---------------------------------------------------------------------------
def test_negative_band_gap_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be non-negative"
        ),
    ):
        calculate_standard_band_edges(
            absolute_electronegativity_ev=(
                5.0
            ),
            band_gap_ev=-1.0,
        )


# ---------------------------------------------------------------------------
# NONPOSITIVE ELECTRONEGATIVITY FAILS
# ---------------------------------------------------------------------------
def test_nonpositive_electronegativity_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be positive"
        ),
    ):
        calculate_standard_band_edges(
            absolute_electronegativity_ev=(
                0.0
            ),
            band_gap_ev=2.0,
        )


# ---------------------------------------------------------------------------
# NEGATIVE TOLERANCE FAILS
# ---------------------------------------------------------------------------
def test_negative_tolerance_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be non-negative"
        ),
    ):
        validate_band_edge_gap(
            cbm_nhe_v=0.0,
            vbm_nhe_v=2.0,
            band_gap_ev=2.0,
            tolerance=-1.0,
        )

