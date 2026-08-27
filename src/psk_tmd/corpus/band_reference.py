from psk_tmd.common.constants import (
    BandReferenceScale,
)


# ---------------------------------------------------------------------------
# REFERENCE CONVERSION CONSTANTS
# ---------------------------------------------------------------------------
AG_AGCL_OFFSETS_V = {
    "saturated_kcl": 0.197,
    "sat_kcl": 0.197,
    "3.5m_kcl": 0.205,
    "3m_kcl": 0.210,
    "1m_kcl": 0.235,
}

DEFAULT_AG_AGCL_DETAIL = (
    "saturated_kcl"
)

SCE_OFFSET_V = 0.244

RHE_PH_SLOPE_V = 0.0591

NHE_VACUUM_LEVEL_EV = 4.44


# ---------------------------------------------------------------------------
# NORMALIZE REFERENCE DETAIL
# ---------------------------------------------------------------------------
def normalize_reference_detail(
    reference_detail: str | None,
) -> str | None:
    if reference_detail is None:
        return None

    normalized = (
        reference_detail
        .strip()
        .lower()
    )

    normalized = (
        normalized
        .replace(" ", "")
        .replace(".", "")
        .replace("-", "")
        .replace("_", "")
    )

    aliases = {
        "saturatedkcl": (
            "saturated_kcl"
        ),
        "satkcl": (
            "sat_kcl"
        ),
        "35mkcl": (
            "3.5m_kcl"
        ),
        "3mkcl": (
            "3m_kcl"
        ),
        "1mkcl": (
            "1m_kcl"
        ),
    }

    return aliases.get(
        normalized,
        reference_detail
        .strip()
        .lower(),
    )


# ---------------------------------------------------------------------------
# GET AG/AGCL OFFSET
# ---------------------------------------------------------------------------
def get_ag_agcl_offset_v(
    reference_detail: str | None,
) -> float:
    normalized_detail = (
        normalize_reference_detail(
            reference_detail
        )
    )

    if normalized_detail is None:
        normalized_detail = (
            DEFAULT_AG_AGCL_DETAIL
        )

    if (
        normalized_detail
        not in AG_AGCL_OFFSETS_V
    ):
        raise ValueError(
            "Unsupported Ag/AgCl "
            "reference detail: "
            f"{reference_detail!r}."
        )

    return AG_AGCL_OFFSETS_V[
        normalized_detail
    ]


# ---------------------------------------------------------------------------
# CONVERT ELECTROCHEMICAL POTENTIAL TO NHE
# ---------------------------------------------------------------------------
def convert_potential_to_nhe(
    value: float,
    reference_scale: (
        BandReferenceScale
    ),
    *,
    reference_detail: (
        str | None
    ) = None,
    ph: float | None = None,
) -> float:
    if (
        reference_scale
        == BandReferenceScale.NHE
    ):
        return value

    if (
        reference_scale
        == BandReferenceScale.SHE
    ):
        return value

    if (
        reference_scale
        == BandReferenceScale.AG_AGCL
    ):
        offset = get_ag_agcl_offset_v(
            reference_detail
        )

        return value + offset

    if (
        reference_scale
        == BandReferenceScale.SCE
    ):
        return value + SCE_OFFSET_V

    if (
        reference_scale
        == BandReferenceScale.RHE
    ):
        if ph is None:
            raise ValueError(
                "pH is required for "
                "RHE to NHE conversion."
            )

        return (
            value
            - RHE_PH_SLOPE_V * ph
        )

    raise ValueError(
        "Unsupported electrochemical "
        "reference scale for NHE "
        f"conversion: {reference_scale.value}."
    )


# ---------------------------------------------------------------------------
# CONVERT VACUUM ENERGY TO NHE
# ---------------------------------------------------------------------------
def convert_vacuum_energy_to_nhe(
    energy_ev: float,
) -> float:
    return (
        -energy_ev
        - NHE_VACUUM_LEVEL_EV
    )

