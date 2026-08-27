import json

from dataclasses import dataclass
from pathlib import Path

from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)
from psk_tmd.corpus.electronegativity import (
    build_element_electronegativity_lookup,
)


# ---------------------------------------------------------------------------
# ELECTRONEGATIVITY COMPARISON
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ElectronegativityComparison:
    element_symbol: str
    canonical_ev: float
    validation_ev: float
    delta_ev: float
    absolute_delta_ev: float
    exceeds_threshold: bool


# ---------------------------------------------------------------------------
# LOAD ELECTRONEGATIVITY REFERENCE
# ---------------------------------------------------------------------------
def load_electronegativity_reference(
    path: Path,
) -> list[
    ElementElectronegativityRecord
]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        payload = json.load(
            file
        )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Electronegativity reference "
            "payload must be an object."
        )

    records_payload = payload.get(
        "records"
    )

    if not isinstance(
        records_payload,
        list,
    ):
        raise ValueError(
            "Electronegativity reference "
            "payload must contain a "
            "'records' list."
        )

    return [
        ElementElectronegativityRecord
        .model_validate(
            record
        )
        for record in records_payload
    ]


# ---------------------------------------------------------------------------
# COMPARE ELECTRONEGATIVITY REFERENCES
# ---------------------------------------------------------------------------
def compare_electronegativity_references(
    canonical_records: list[
        ElementElectronegativityRecord
    ],
    validation_records: list[
        ElementElectronegativityRecord
    ],
    *,
    discrepancy_threshold_ev: float,
) -> list[
    ElectronegativityComparison
]:
    if discrepancy_threshold_ev < 0.0:
        raise ValueError(
            "Discrepancy threshold must be "
            "non-negative."
        )

    canonical_lookup = (
        build_element_electronegativity_lookup(
            canonical_records
        )
    )

    validation_lookup = (
        build_element_electronegativity_lookup(
            validation_records
        )
    )

    comparisons: list[
        ElectronegativityComparison
    ] = []

    common_symbols = sorted(
        set(
            canonical_lookup
        )
        & set(
            validation_lookup
        )
    )

    for symbol in common_symbols:
        canonical_value = (
            canonical_lookup[
                symbol
            ].absolute_electronegativity_ev
        )

        validation_value = (
            validation_lookup[
                symbol
            ].absolute_electronegativity_ev
        )

        if (
            canonical_value is None
            or validation_value is None
        ):
            continue

        delta_ev = (
            canonical_value
            - validation_value
        )

        absolute_delta_ev = abs(
            delta_ev
        )

        comparisons.append(
            ElectronegativityComparison(
                element_symbol=symbol,
                canonical_ev=(
                    canonical_value
                ),
                validation_ev=(
                    validation_value
                ),
                delta_ev=(
                    delta_ev
                ),
                absolute_delta_ev=(
                    absolute_delta_ev
                ),
                exceeds_threshold=(
                    absolute_delta_ev
                    > discrepancy_threshold_ev
                ),
            )
        )

    return comparisons


# ---------------------------------------------------------------------------
# GET FLAGGED COMPARISONS
# ---------------------------------------------------------------------------
def get_flagged_comparisons(
    comparisons: list[
        ElectronegativityComparison
    ],
) -> list[
    ElectronegativityComparison
]:
    return [
        comparison
        for comparison in comparisons
        if comparison.exceeds_threshold
    ]


