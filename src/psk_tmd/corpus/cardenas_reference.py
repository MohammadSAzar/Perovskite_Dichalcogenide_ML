from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)


# ---------------------------------------------------------------------------
# CARDENAS REFERENCE METADATA
# ---------------------------------------------------------------------------
CARDENAS_SOURCE_NAME = (
    "Cardenas et al. 2016"
)

CARDENAS_SOURCE_REFERENCE = (
    "10.1039/C6CP04533B"
)

CARDENAS_METHOD = (
    "Benchmark neutral chemical potential "
    "from Cardenas et al. 2016 Table 3; "
    "absolute electronegativity = -mu."
)


# ---------------------------------------------------------------------------
# CARDENAS NEUTRAL CHEMICAL POTENTIALS
# ---------------------------------------------------------------------------
CARDENAS_NEUTRAL_CHEMICAL_POTENTIAL_EV = {
    "H": -7.18,
    "He": -12.29,
    "Li": -3.00,
    "Be": -4.66,
    "B": -4.29,
    "C": -6.26,
    "N": -7.27,
    "O": -7.54,
    "F": -10.41,
    "Ne": -10.78,
    "Na": -2.84,
    "Mg": -3.82,
    "Al": -3.21,
    "Si": -4.77,
    "P": -5.62,
    "S": -6.22,
    "Cl": -8.29,
    "Ar": -7.88,
    "K": -2.42,
    "Ca": -3.07,
    "Sc": -3.38,
    "Ti": -3.45,
    "V": -3.64,
    "Cr": -3.72,
    "Mn": -3.72,
    "Fe": -4.03,
    "Co": -4.27,
    "Ni": -4.40,
    "Cu": -4.48,
    "Zn": -4.70,
    "Ga": -3.21,
    "Ge": -4.57,
    "As": -5.30,
    "Se": -5.88,
    "Br": -7.59,
    "Kr": -7.00,
    "Rb": -2.33,
    "Sr": -2.88,
    "Y": -3.27,
    "Zr": -3.53,
    "Nb": -3.83,
    "Mo": -3.92,
    "Tc": -3.91,
    "Ru": -4.22,
    "Rh": -4.30,
    "Pd": -4.44,
    "Ag": -4.44,
    "Cd": -4.50,
    "In": -3.09,
    "Sn": -4.23,
    "Sb": -4.82,
    "Te": -5.49,
    "I": -6.75,
    "Xe": -6.07,
    "Cs": -2.18,
    "Ba": -2.68,
    "La": -3.03,
    "Ce": -3.09,
    "Pr": -3.22,
    "Nd": -2.85,
    "Pm": -2.86,
    "Sm": -2.91,
    "Eu": -2.90,
    "Gd": -3.15,
    "Tb": -3.15,
    "Dy": -3.15,
    "Ho": -3.18,
    "Er": -3.21,
    "Tm": -3.10,
    "Yb": -3.13,
    "Lu": -2.88,
    "Hf": -3.47,
    "Ta": -3.94,
    "W": -4.35,
    "Re": -4.00,
    "Os": -4.76,
    "Ir": -5.27,
    "Pt": -5.54,
    "Au": -5.77,
    "Hg": -5.22,
    "Tl": -3.24,
    "Pb": -3.88,
    "Bi": -4.12,
    "Po": -5.15,
    "At": -6.05,
    "Rn": -5.38,
    "Fr": -2.28,
    "Ra": -2.69,
    "Ac": -2.76,
    "Th": -3.35,
    "Pa": -3.14,
    "U": -3.29,
    "Np": -3.29,
    "Pu": -3.07,
    "Am": -3.03,
    "Cm": -3.16,
    "Bk": -3.12,
}


# ---------------------------------------------------------------------------
# BUILD CARDENAS ELEMENT RECORD
# ---------------------------------------------------------------------------
def build_cardenas_element_record(
    element_symbol: str,
    chemical_potential_ev: float,
) -> ElementElectronegativityRecord:
    if chemical_potential_ev >= 0.0:
        raise ValueError(
            "Neutral chemical potential "
            "must be negative for the "
            "Cardenas elemental reference."
        )

    absolute_electronegativity_ev = (
        -chemical_potential_ev
    )

    return (
        ElementElectronegativityRecord(
            element_symbol=(
                element_symbol
            ),
            chemical_potential_ev=(
                chemical_potential_ev
            ),
            absolute_electronegativity_ev=(
                absolute_electronegativity_ev
            ),
            value_status=(
                ElectronegativityValueStatus
                .TABULATED
            ),
            ionization_energy_ev=None,
            electron_affinity_ev=None,
            source_name=(
                CARDENAS_SOURCE_NAME
            ),
            source_reference=(
                CARDENAS_SOURCE_REFERENCE
            ),
            estimation_method=(
                CARDENAS_METHOD
            ),
            notes=(
                "Canonical elemental "
                "absolute electronegativity "
                "for standardized band-edge "
                "calculations."
            ),
        )
    )


# ---------------------------------------------------------------------------
# BUILD CARDENAS REFERENCE
# ---------------------------------------------------------------------------
def build_cardenas_reference(
) -> list[
    ElementElectronegativityRecord
]:
    return [
        build_cardenas_element_record(
            element_symbol=(
                element_symbol
            ),
            chemical_potential_ev=(
                chemical_potential_ev
            ),
        )
        for (
            element_symbol,
            chemical_potential_ev,
        )
        in (
            CARDENAS_NEUTRAL_CHEMICAL_POTENTIAL_EV
            .items()
        )
    ]


# ---------------------------------------------------------------------------
# BUILD CARDENAS LOOKUP
# ---------------------------------------------------------------------------
def build_cardenas_lookup(
) -> dict[
    str,
    ElementElectronegativityRecord,
]:
    records = (
        build_cardenas_reference()
    )

    return {
        record.element_symbol: record
        for record in records
    }

