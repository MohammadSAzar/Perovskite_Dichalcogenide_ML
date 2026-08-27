from psk_tmd.corpus.cardenas_reference import (
    build_cardenas_lookup,
)
from psk_tmd.corpus.compound_electronegativity import (
    calculate_compound_absolute_electronegativity,
)


# ---------------------------------------------------------------------------
# MATERIAL COMPOSITIONS
# ---------------------------------------------------------------------------
MATERIALS = {
    "CaTiO3": {
        "Ca": 1.0,
        "Ti": 1.0,
        "O": 3.0,
    },
    "LaNiO3": {
        "La": 1.0,
        "Ni": 1.0,
        "O": 3.0,
    },
    "PbTiO3": {
        "Pb": 1.0,
        "Ti": 1.0,
        "O": 3.0,
    },
    "MoS2": {
        "Mo": 1.0,
        "S": 2.0,
    },
    "WS2": {
        "W": 1.0,
        "S": 2.0,
    },
}


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    lookup = (
        build_cardenas_lookup()
    )

    print(
        "COMPOUND ABSOLUTE "
        "ELECTRONEGATIVITY"
    )
    print(
        "-" * 70
    )

    for (
        formula,
        composition,
    ) in MATERIALS.items():
        value = (
            calculate_compound_absolute_electronegativity(
                composition=composition,
                elemental_lookup=lookup,
            )
        )

        print(
            f"{formula:<10} "
            f"{value:.4f} eV"
        )


if __name__ == "__main__":
    main()

