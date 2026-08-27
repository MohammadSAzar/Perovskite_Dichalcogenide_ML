import math

from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)


# ---------------------------------------------------------------------------
# VALIDATE COMPOSITION
# ---------------------------------------------------------------------------
def validate_composition(
    composition: dict[
        str,
        float,
    ],
) -> None:
    if not composition:
        raise ValueError(
            "Composition must contain "
            "at least one element."
        )

    for (
        element_symbol,
        coefficient,
    ) in composition.items():
        if not element_symbol:
            raise ValueError(
                "Element symbol must not "
                "be empty."
            )

        if coefficient <= 0.0:
            raise ValueError(
                "Stoichiometric coefficient "
                "must be positive for "
                f"{element_symbol!r}."
            )


# ---------------------------------------------------------------------------
# BUILD ANION-SUBSTITUTED COMPOSITION
# ---------------------------------------------------------------------------
def build_anion_substituted_composition(
    *,
    non_anion_composition: dict[
        str,
        float,
    ],
    host_anion_symbol: str,
    host_anion_total: float,
    anion_dopants: dict[
        str,
        float,
    ] | None = None,
) -> dict[
    str,
    float,
]:
    validate_composition(
        non_anion_composition
    )

    if not host_anion_symbol:
        raise ValueError(
            "Host anion symbol must not "
            "be empty."
        )

    if host_anion_total <= 0.0:
        raise ValueError(
            "Host anion total must be "
            "positive."
        )

    dopants = (
        anion_dopants
        if anion_dopants is not None
        else {}
    )

    total_dopant_amount = 0.0

    for (
        dopant_symbol,
        coefficient,
    ) in dopants.items():
        if not dopant_symbol:
            raise ValueError(
                "Anion dopant symbol must "
                "not be empty."
            )

        if (
            dopant_symbol
            == host_anion_symbol
        ):
            raise ValueError(
                "Anion dopant must differ "
                "from the host anion "
                f"{host_anion_symbol!r}."
            )

        if coefficient <= 0.0:
            raise ValueError(
                "Anion dopant coefficient "
                "must be positive for "
                f"{dopant_symbol!r}."
            )

        total_dopant_amount += (
            coefficient
        )

    if (
        total_dopant_amount
        > host_anion_total
    ):
        raise ValueError(
            "Total anion dopant amount "
            "cannot exceed the available "
            "anion sublattice."
        )

    host_anion_remaining = (
        host_anion_total
        - total_dopant_amount
    )

    composition = dict(
        non_anion_composition
    )

    if host_anion_remaining > 0.0:
        composition[
            host_anion_symbol
        ] = host_anion_remaining

    for (
        dopant_symbol,
        coefficient,
    ) in dopants.items():
        composition[
            dopant_symbol
        ] = coefficient

    return composition


# ---------------------------------------------------------------------------
# BUILD PSK ANION-DOPED COMPOSITION
# ---------------------------------------------------------------------------
def build_psk_anion_doped_composition(
    *,
    cation_composition: dict[
        str,
        float,
    ],
    anion_dopants: dict[
        str,
        float,
    ] | None = None,
) -> dict[
    str,
    float,
]:
    return (
        build_anion_substituted_composition(
            non_anion_composition=(
                cation_composition
            ),
            host_anion_symbol="O",
            host_anion_total=3.0,
            anion_dopants=(
                anion_dopants
            ),
        )
    )


# ---------------------------------------------------------------------------
# BUILD TMD ANION-DOPED COMPOSITION
# ---------------------------------------------------------------------------
def build_tmd_anion_doped_composition(
    *,
    metal_composition: dict[
        str,
        float,
    ],
    host_chalcogen_symbol: str,
    anion_dopants: dict[
        str,
        float,
    ] | None = None,
) -> dict[
    str,
    float,
]:
    return (
        build_anion_substituted_composition(
            non_anion_composition=(
                metal_composition
            ),
            host_anion_symbol=(
                host_chalcogen_symbol
            ),
            host_anion_total=2.0,
            anion_dopants=(
                anion_dopants
            ),
        )
    )


# ---------------------------------------------------------------------------
# CALCULATE COMPOUND ABSOLUTE ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def calculate_compound_absolute_electronegativity(
    composition: dict[
        str,
        float,
    ],
    elemental_lookup: dict[
        str,
        ElementElectronegativityRecord,
    ],
) -> float:
    validate_composition(
        composition
    )

    total_coefficient = sum(
        composition.values()
    )

    weighted_log_sum = 0.0

    for (
        element_symbol,
        coefficient,
    ) in composition.items():
        record = elemental_lookup.get(
            element_symbol
        )

        if record is None:
            raise ValueError(
                "No elemental "
                "electronegativity record "
                "for "
                f"{element_symbol!r}."
            )

        value = (
            record
            .absolute_electronegativity_ev
        )

        if value is None:
            raise ValueError(
                "Absolute electronegativity "
                "is unavailable for "
                f"{element_symbol!r}."
            )

        if value <= 0.0:
            raise ValueError(
                "Absolute electronegativity "
                "must be positive for "
                f"{element_symbol!r}."
            )

        weighted_log_sum += (
            coefficient
            * math.log(
                value
            )
        )

    return math.exp(
        weighted_log_sum
        / total_coefficient
    )

