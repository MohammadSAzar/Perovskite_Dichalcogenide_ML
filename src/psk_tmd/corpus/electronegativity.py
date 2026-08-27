from typing import Any

from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)


# ---------------------------------------------------------------------------
# PUBCHEM COLUMN NAMES
# ---------------------------------------------------------------------------
PUBCHEM_SYMBOL = (
    "Symbol"
)

PUBCHEM_IONIZATION_ENERGY = (
    "IonizationEnergy"
)

PUBCHEM_ELECTRON_AFFINITY = (
    "ElectronAffinity"
)

PUBCHEM_SOURCE_NAME = (
    "PubChem Periodic Table"
)


# ---------------------------------------------------------------------------
# PARSE OPTIONAL FLOAT
# ---------------------------------------------------------------------------
def parse_optional_float(
    value: Any,
) -> float | None:
    if value is None:
        return None

    if isinstance(
        value,
        str,
    ):
        value = value.strip()

        if not value:
            return None

    try:
        return float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "Could not parse numeric value: "
            f"{value!r}."
        ) from error


# ---------------------------------------------------------------------------
# CALCULATE ATOMIC ABSOLUTE ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def calculate_atomic_absolute_electronegativity(
    ionization_energy_ev: float,
    electron_affinity_ev: float,
) -> float:
    if ionization_energy_ev < 0.0:
        raise ValueError(
            "Ionization energy must be "
            "non-negative."
        )

    return (
        ionization_energy_ev
        + electron_affinity_ev
    ) / 2.0


# ---------------------------------------------------------------------------
# CALCULATE CHEMICAL POTENTIAL
# ---------------------------------------------------------------------------
def calculate_atomic_chemical_potential(
    ionization_energy_ev: float,
    electron_affinity_ev: float,
) -> float:
    absolute_electronegativity_ev = (
        calculate_atomic_absolute_electronegativity(
            ionization_energy_ev=(
                ionization_energy_ev
            ),
            electron_affinity_ev=(
                electron_affinity_ev
            ),
        )
    )

    return (
        -absolute_electronegativity_ev
    )


# ---------------------------------------------------------------------------
# BUILD PUBCHEM COLUMN LOOKUP
# ---------------------------------------------------------------------------
def build_pubchem_column_lookup(
    payload: dict[
        str,
        Any,
    ],
) -> dict[
    str,
    int,
]:
    try:
        columns = (
            payload[
                "Table"
            ][
                "Columns"
            ][
                "Column"
            ]
        )
    except (
        KeyError,
        TypeError,
    ) as error:
        raise ValueError(
            "Invalid PubChem periodic-table "
            "payload: missing columns."
        ) from error

    if not isinstance(
        columns,
        list,
    ):
        raise ValueError(
            "Invalid PubChem periodic-table "
            "payload: columns must be a list."
        )

    return {
        str(
            column_name
        ): index
        for index, column_name
        in enumerate(
            columns
        )
    }


# ---------------------------------------------------------------------------
# GET REQUIRED PUBCHEM COLUMN INDEX
# ---------------------------------------------------------------------------
def get_required_column_index(
    column_lookup: dict[
        str,
        int,
    ],
    column_name: str,
) -> int:
    if (
        column_name
        not in column_lookup
    ):
        raise ValueError(
            "PubChem periodic-table payload "
            "is missing required column "
            f"{column_name!r}."
        )

    return column_lookup[
        column_name
    ]


# ---------------------------------------------------------------------------
# BUILD PUBCHEM ELEMENT RECORD
# ---------------------------------------------------------------------------
def build_element_electronegativity_record(
    *,
    element_symbol: str,
    ionization_energy_ev: (
        float | None
    ),
    electron_affinity_ev: (
        float | None
    ),
    source_reference: (
        str | None
    ),
) -> ElementElectronegativityRecord:
    if (
        ionization_energy_ev is None
        or electron_affinity_ev is None
    ):
        return (
            ElementElectronegativityRecord(
                element_symbol=(
                    element_symbol
                ),
                chemical_potential_ev=None,
                absolute_electronegativity_ev=(
                    None
                ),
                value_status=(
                    ElectronegativityValueStatus
                    .UNAVAILABLE
                ),
                ionization_energy_ev=(
                    ionization_energy_ev
                ),
                electron_affinity_ev=(
                    electron_affinity_ev
                ),
                source_name=(
                    PUBCHEM_SOURCE_NAME
                ),
                source_reference=(
                    source_reference
                ),
                estimation_method=None,
                notes=None,
            )
        )

    absolute_electronegativity_ev = (
        calculate_atomic_absolute_electronegativity(
            ionization_energy_ev=(
                ionization_energy_ev
            ),
            electron_affinity_ev=(
                electron_affinity_ev
            ),
        )
    )

    chemical_potential_ev = (
        calculate_atomic_chemical_potential(
            ionization_energy_ev=(
                ionization_energy_ev
            ),
            electron_affinity_ev=(
                electron_affinity_ev
            ),
        )
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
                .DERIVED_IE_EA
            ),
            ionization_energy_ev=(
                ionization_energy_ev
            ),
            electron_affinity_ev=(
                electron_affinity_ev
            ),
            source_name=(
                PUBCHEM_SOURCE_NAME
            ),
            source_reference=(
                source_reference
            ),
            estimation_method=None,
            notes=None,
        )
    )


# ---------------------------------------------------------------------------
# PARSE PUBCHEM PERIODIC TABLE
# ---------------------------------------------------------------------------
def parse_pubchem_periodic_table(
    payload: dict[
        str,
        Any,
    ],
    *,
    source_reference: (
        str | None
    ) = None,
) -> list[
    ElementElectronegativityRecord
]:
    column_lookup = (
        build_pubchem_column_lookup(
            payload
        )
    )

    symbol_index = (
        get_required_column_index(
            column_lookup,
            PUBCHEM_SYMBOL,
        )
    )

    ionization_index = (
        get_required_column_index(
            column_lookup,
            PUBCHEM_IONIZATION_ENERGY,
        )
    )

    affinity_index = (
        get_required_column_index(
            column_lookup,
            PUBCHEM_ELECTRON_AFFINITY,
        )
    )

    try:
        rows = (
            payload[
                "Table"
            ][
                "Row"
            ]
        )
    except (
        KeyError,
        TypeError,
    ) as error:
        raise ValueError(
            "Invalid PubChem periodic-table "
            "payload: missing rows."
        ) from error

    if not isinstance(
        rows,
        list,
    ):
        raise ValueError(
            "Invalid PubChem periodic-table "
            "payload: rows must be a list."
        )

    records: list[
        ElementElectronegativityRecord
    ] = []

    for row in rows:
        try:
            cells = row[
                "Cell"
            ]

            symbol = str(
                cells[
                    symbol_index
                ]
            ).strip()

            ionization_energy_ev = (
                parse_optional_float(
                    cells[
                        ionization_index
                    ]
                )
            )

            electron_affinity_ev = (
                parse_optional_float(
                    cells[
                        affinity_index
                    ]
                )
            )

        except (
            KeyError,
            IndexError,
            TypeError,
        ) as error:
            raise ValueError(
                "Invalid PubChem "
                "periodic-table row."
            ) from error

        if not symbol:
            raise ValueError(
                "PubChem periodic-table row "
                "has an empty element symbol."
            )

        records.append(
            build_element_electronegativity_record(
                element_symbol=symbol,
                ionization_energy_ev=(
                    ionization_energy_ev
                ),
                electron_affinity_ev=(
                    electron_affinity_ev
                ),
                source_reference=(
                    source_reference
                ),
            )
        )

    return records


# ---------------------------------------------------------------------------
# BUILD ELEMENT LOOKUP
# ---------------------------------------------------------------------------
def build_element_electronegativity_lookup(
    records: list[
        ElementElectronegativityRecord
    ],
) -> dict[
    str,
    ElementElectronegativityRecord,
]:
    lookup: dict[
        str,
        ElementElectronegativityRecord,
    ] = {}

    for record in records:
        symbol = (
            record.element_symbol
        )

        if symbol in lookup:
            raise ValueError(
                "Duplicate elemental "
                "electronegativity record "
                f"for {symbol}."
            )

        lookup[
            symbol
        ] = record

    return lookup


# ---------------------------------------------------------------------------
# BUILD ELECTRONEGATIVITY REFERENCE PAYLOAD
# ---------------------------------------------------------------------------
def build_electronegativity_reference_payload(
    payload: dict[
        str,
        Any,
    ],
    *,
    source_url: str,
    retrieval_date: str,
) -> dict:
    records = (
        parse_pubchem_periodic_table(
            payload,
            source_reference=(
                source_url
            ),
        )
    )

    return {
        "source_name": (
            PUBCHEM_SOURCE_NAME
        ),
        "source_url": source_url,
        "retrieval_date": retrieval_date,
        "method": (
            "absolute electronegativity "
            "derived as (IE + EA) / 2; "
            "chemical potential derived "
            "as -(IE + EA) / 2"
        ),
        "records": [
            record.model_dump(
                mode="json"
            )
            for record in records
        ],
    }


# ---------------------------------------------------------------------------
# RESOLVE ELEMENT ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def resolve_element_electronegativity(
    primary: (
        ElementElectronegativityRecord
    ),
    fallback: (
        ElementElectronegativityRecord
        | None
    ) = None,
) -> ElementElectronegativityRecord:
    if (
        fallback is not None
        and fallback.element_symbol
        != primary.element_symbol
    ):
        raise ValueError(
            "Primary and fallback element "
            "symbols do not match: "
            f"{primary.element_symbol!r} "
            "!= "
            f"{fallback.element_symbol!r}."
        )

    if (
        primary.absolute_electronegativity_ev
        is not None
    ):
        return primary

    if fallback is None:
        return primary

    if (
        fallback.absolute_electronegativity_ev
        is None
    ):
        return primary

    return fallback


# ---------------------------------------------------------------------------
# MERGE ELECTRONEGATIVITY REFERENCES
# ---------------------------------------------------------------------------
def merge_electronegativity_references(
    primary_records: list[
        ElementElectronegativityRecord
    ],
    fallback_records: list[
        ElementElectronegativityRecord
    ],
) -> list[
    ElementElectronegativityRecord
]:
    primary_lookup = (
        build_element_electronegativity_lookup(
            primary_records
        )
    )

    fallback_lookup = (
        build_element_electronegativity_lookup(
            fallback_records
        )
    )

    extra_fallback_symbols = (
        set(
            fallback_lookup
        )
        - set(
            primary_lookup
        )
    )

    if extra_fallback_symbols:
        extra = ", ".join(
            sorted(
                extra_fallback_symbols
            )
        )

        raise ValueError(
            "Fallback reference contains "
            "elements missing from the "
            f"primary reference: {extra}"
        )

    resolved: list[
        ElementElectronegativityRecord
    ] = []

    for primary in primary_records:
        fallback = (
            fallback_lookup.get(
                primary.element_symbol
            )
        )

        resolved.append(
            resolve_element_electronegativity(
                primary=primary,
                fallback=fallback,
            )
        )

    return resolved

