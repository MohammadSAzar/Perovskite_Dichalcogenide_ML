import json

from copy import deepcopy
from pathlib import Path

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
    MaterialBandRecord,
)
from psk_tmd.corpus.material_band_calculation import (
    standardize_material_band_record,
)


# ---------------------------------------------------------------------------
# INPUT PATH
# ---------------------------------------------------------------------------
INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "pilot_v0_3"
    / "material_band_records.json"
)


# ---------------------------------------------------------------------------
# OUTPUT PATH
# ---------------------------------------------------------------------------
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "pilot_v0_3"
    / "material_band_records_standardized.json"
)


# ---------------------------------------------------------------------------
# CARDENAS REFERENCE PATH
# ---------------------------------------------------------------------------
CARDENAS_PATH = (
    PROJECT_ROOT
    / "data"
    / "external"
    / "electronegativity"
    / "cardenas2016_absolute_electronegativity.json"
)


# ---------------------------------------------------------------------------
# PILOT COMPOSITIONS
# ---------------------------------------------------------------------------
PILOT_COMPOSITIONS: dict[
    str,
    dict[
        str,
        float,
    ],
] = {
    "LaNiO3": {
        "La": 1.0,
        "Ni": 1.0,
        "O": 3.0,
    },
    "MoS2": {
        "Mo": 1.0,
        "S": 2.0,
    },
    "CaTiO3": {
        "Ca": 1.0,
        "Ti": 1.0,
        "O": 3.0,
    },
    "WS2": {
        "W": 1.0,
        "S": 2.0,
    },
    "PbTiO3": {
        "Pb": 1.0,
        "Ti": 1.0,
        "O": 3.0,
    },
}


# ---------------------------------------------------------------------------
# REPORTED FIELDS
# ---------------------------------------------------------------------------
REPORTED_FIELDS = (
    "reported_band_gap_ev",
    "band_gap_type",
    "band_gap_method",
    "reported_cbm",
    "reported_vbm",
    "reported_reference_scale",
    "reported_reference_detail",
    "reported_ph",
    "reported_cbm_nhe_v",
    "reported_vbm_nhe_v",
    "claim_context",
    "source_location",
    "source_text",
)


# ---------------------------------------------------------------------------
# LOAD MATERIAL BAND RECORDS
# ---------------------------------------------------------------------------
def load_material_band_records(
    path: Path,
) -> list[
    MaterialBandRecord
]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        payload,
        list,
    ):
        raise ValueError(
            "Material band record file "
            "must contain a JSON list."
        )

    return [
        MaterialBandRecord.model_validate(
            item
        )
        for item in payload
    ]


# ---------------------------------------------------------------------------
# LOAD CARDENAS LOOKUP
# ---------------------------------------------------------------------------
def load_cardenas_lookup(
    path: Path,
) -> dict[
    str,
    ElementElectronegativityRecord,
]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if (
        payload.get(
            "canonical_for_band_calculation"
        )
        is not True
    ):
        raise ValueError(
            "Cárdenas reference is not marked "
            "canonical for band calculation."
        )

    records = payload.get(
        "records"
    )

    if not isinstance(
        records,
        list,
    ):
        raise ValueError(
            "Cárdenas reference is missing "
            "its records list."
        )

    lookup: dict[
        str,
        ElementElectronegativityRecord,
    ] = {}

    for item in records:
        record = (
            ElementElectronegativityRecord
            .model_validate(
                item
            )
        )

        if (
            record.element_symbol
            in lookup
        ):
            raise ValueError(
                "Duplicate Cárdenas element: "
                f"{record.element_symbol}"
            )

        lookup[
            record.element_symbol
        ] = record

    return lookup


# ---------------------------------------------------------------------------
# GET RECORD FORMULA
# ---------------------------------------------------------------------------
def get_record_formula(
    record: MaterialBandRecord,
) -> str:
    return (
        record.formula_normalized
        or record.formula_reported
    )


# ---------------------------------------------------------------------------
# GET PILOT COMPOSITION
# ---------------------------------------------------------------------------
def get_pilot_composition(
    record: MaterialBandRecord,
) -> dict[
    str,
    float,
]:
    formula = (
        get_record_formula(
            record
        )
    )

    composition = (
        PILOT_COMPOSITIONS.get(
            formula
        )
    )

    if composition is None:
        raise ValueError(
            f"No pilot composition configured "
            f"for {formula}."
        )

    return composition


# ---------------------------------------------------------------------------
# SNAPSHOT REPORTED FIELDS
# ---------------------------------------------------------------------------
def snapshot_reported_fields(
    record: MaterialBandRecord,
) -> dict[
    str,
    object,
]:
    return {
        field_name: deepcopy(
            getattr(
                record,
                field_name,
            )
        )
        for field_name
        in REPORTED_FIELDS
    }


# ---------------------------------------------------------------------------
# VALIDATE REPORTED FIELDS UNCHANGED
# ---------------------------------------------------------------------------
def validate_reported_fields_unchanged(
    before: dict[
        str,
        object,
    ],
    after: MaterialBandRecord,
) -> None:
    for (
        field_name,
        original_value,
    ) in before.items():
        standardized_value = getattr(
            after,
            field_name,
        )

        if (
            standardized_value
            != original_value
        ):
            raise ValueError(
                f"{after.band_record_id}: "
                f"standardization modified "
                f"reported field "
                f"{field_name!r}: "
                f"{original_value!r} -> "
                f"{standardized_value!r}"
            )


# ---------------------------------------------------------------------------
# VALIDATE STANDARDIZED RECORD
# ---------------------------------------------------------------------------
def validate_standardized_record(
    record: MaterialBandRecord,
) -> None:
    if (
        record.absolute_electronegativity_ev
        is None
    ):
        raise ValueError(
            f"{record.band_record_id}: "
            "missing compound absolute "
            "electronegativity."
        )

    if (
        record.calculated_cbm_nhe_v
        is None
    ):
        raise ValueError(
            f"{record.band_record_id}: "
            "missing standardized CBM."
        )

    if (
        record.calculated_vbm_nhe_v
        is None
    ):
        raise ValueError(
            f"{record.band_record_id}: "
            "missing standardized VBM."
        )

    if (
        record.reported_band_gap_ev
        is None
    ):
        raise ValueError(
            f"{record.band_record_id}: "
            "missing reported Eg required "
            "for standard calculation."
        )

    calculated_gap = (
        record.calculated_vbm_nhe_v
        - record.calculated_cbm_nhe_v
    )

    if abs(
        calculated_gap
        - record.reported_band_gap_ev
    ) > 1e-8:
        raise ValueError(
            f"{record.band_record_id}: "
            "standardized band-edge gap "
            "does not reproduce reported Eg."
        )


# ---------------------------------------------------------------------------
# STANDARDIZE RECORD
# ---------------------------------------------------------------------------
def standardize_record(
    record: MaterialBandRecord,
    *,
    elemental_lookup: dict[
        str,
        ElementElectronegativityRecord,
    ],
) -> MaterialBandRecord:
    reported_snapshot = (
        snapshot_reported_fields(
            record
        )
    )

    composition = (
        get_pilot_composition(
            record
        )
    )

    standardized = (
        standardize_material_band_record(
            record,
            composition=composition,
            elemental_lookup=(
                elemental_lookup
            ),
        )
    )

    validate_reported_fields_unchanged(
        reported_snapshot,
        standardized,
    )

    validate_standardized_record(
        standardized
    )

    return standardized


# ---------------------------------------------------------------------------
# STANDARDIZE PILOT RECORDS
# ---------------------------------------------------------------------------
def standardize_pilot_records(
    records: list[
        MaterialBandRecord
    ],
    *,
    elemental_lookup: dict[
        str,
        ElementElectronegativityRecord,
    ],
) -> list[
    MaterialBandRecord
]:
    standardized_records = [
        standardize_record(
            record,
            elemental_lookup=(
                elemental_lookup
            ),
        )
        for record in records
    ]

    if len(
        standardized_records
    ) != 8:
        raise ValueError(
            "Pilot must contain exactly "
            "8 standardized band records."
        )

    return standardized_records


# ---------------------------------------------------------------------------
# SAVE RECORDS
# ---------------------------------------------------------------------------
def save_records(
    records: list[
        MaterialBandRecord
    ],
    *,
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = [
        record.model_dump(
            mode="json"
        )
        for record in records
    ]

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# FORMAT OPTIONAL FLOAT
# ---------------------------------------------------------------------------
def format_optional_float(
    value: float | None,
) -> str:
    if value is None:
        return "-"

    return (
        f"{value:.4f}"
    )


# ---------------------------------------------------------------------------
# PRINT RECORD
# ---------------------------------------------------------------------------
def print_record(
    record: MaterialBandRecord,
) -> None:
    print(
        f"{record.paper_id:<9} "
        f"{record.pair_id:<10} "
        f"{record.formula_reported:<8} "
        f"Eg={record.reported_band_gap_ev:>5.2f} "
        f"chi={format_optional_float(record.absolute_electronegativity_ev):>7} "
        f"| reported "
        f"CB={format_optional_float(record.reported_cbm):>7} "
        f"VB={format_optional_float(record.reported_vbm):>7} "
        f"| standardized "
        f"CB={format_optional_float(record.calculated_cbm_nhe_v):>7} "
        f"VB={format_optional_float(record.calculated_vbm_nhe_v):>7}"
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        load_material_band_records(
            INPUT_PATH
        )
    )

    elemental_lookup = (
        load_cardenas_lookup(
            CARDENAS_PATH
        )
    )

    standardized_records = (
        standardize_pilot_records(
            records,
            elemental_lookup=(
                elemental_lookup
            ),
        )
    )

    print(
        "PILOT STANDARDIZED MATERIAL BAND RECORDS"
    )
    print(
        "=" * 120
    )

    for record in standardized_records:
        print_record(
            record
        )

    print(
        "-" * 120
    )
    print(
        f"records="
        f"{len(standardized_records)}"
    )

    save_records(
        standardized_records,
        path=OUTPUT_PATH,
    )

    print(
        f"saved={OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()

