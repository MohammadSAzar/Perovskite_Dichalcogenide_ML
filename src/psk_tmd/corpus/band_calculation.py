# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
FREE_ELECTRON_ENERGY_EV = 4.5


# ---------------------------------------------------------------------------
# CALCULATE STANDARD BAND EDGES
# ---------------------------------------------------------------------------
def calculate_standard_band_edges(
    *,
    absolute_electronegativity_ev: float,
    band_gap_ev: float,
    free_electron_energy_ev: float = (
        FREE_ELECTRON_ENERGY_EV
    ),
) -> tuple[
    float,
    float,
]:
    if absolute_electronegativity_ev <= 0.0:
        raise ValueError(
            "Absolute electronegativity "
            "must be positive."
        )

    if band_gap_ev < 0.0:
        raise ValueError(
            "Band gap must be "
            "non-negative."
        )

    cbm_nhe_v = (
        absolute_electronegativity_ev
        - free_electron_energy_ev
        - band_gap_ev / 2.0
    )

    vbm_nhe_v = (
        absolute_electronegativity_ev
        - free_electron_energy_ev
        + band_gap_ev / 2.0
    )

    return (
        cbm_nhe_v,
        vbm_nhe_v,
    )


# ---------------------------------------------------------------------------
# VALIDATE BAND EDGE GAP
# ---------------------------------------------------------------------------
def validate_band_edge_gap(
    *,
    cbm_nhe_v: float,
    vbm_nhe_v: float,
    band_gap_ev: float,
    tolerance: float = 1e-8,
) -> None:
    if tolerance < 0.0:
        raise ValueError(
            "Tolerance must be "
            "non-negative."
        )

    calculated_gap = (
        vbm_nhe_v
        - cbm_nhe_v
    )

    if abs(
        calculated_gap
        - band_gap_ev
    ) > tolerance:
        raise ValueError(
            "Band-edge difference does "
            "not match the band gap."
        )

