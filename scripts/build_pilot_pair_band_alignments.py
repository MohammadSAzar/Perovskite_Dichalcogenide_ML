import json

from dataclasses import dataclass
from pathlib import Path

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.common.constants import (
    ChargeTransferClass,
    ManualReviewStatus,
)
from psk_tmd.common.models import (
    MaterialBandRecord,
    PairBandAlignmentRecord,
)
from psk_tmd.corpus.pair_band_alignment import (
    build_pair_band_alignment,
    is_band_offset_eligible,
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
    / "material_band_records_standardized.json"
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
    / "pair_band_alignments.json"
)


# ---------------------------------------------------------------------------
# PILOT PAIR DEFINITION
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilotPairDefinition:
    pair_id: str
    charge_transfer_class: ChargeTransferClass
    oxidation_formula: str | None
    reduction_formula: str | None
    role_assignment_basis: str | None


# ---------------------------------------------------------------------------
# PILOT PAIR DEFINITIONS
# ---------------------------------------------------------------------------
PILOT_PAIR_DEFINITIONS = [
    PilotPairDefinition(
        pair_id="PAIR-0001",
        charge_transfer_class=(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        ),
        oxidation_formula="PbTiO3",
        reduction_formula="MoS2",
        role_assignment_basis=(
            "Curated S-scheme mechanism: "
            "PbTiO3 is the oxidation "
            "photocatalyst and MoS2 is "
            "the reduction photocatalyst."
        ),
    ),
    PilotPairDefinition(
        pair_id="PAIR-0002",
        charge_transfer_class=(
            ChargeTransferClass.TYPE_I
        ),
        oxidation_formula=None,
        reduction_formula=None,
        role_assignment_basis=None,
    ),
    PilotPairDefinition(
        pair_id="PAIR-0003",
        charge_transfer_class=(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        ),
        oxidation_formula="CaTiO3",
        reduction_formula="MoS2",
        role_assignment_basis=(
            "Curated Z-scheme mechanism: "
            "CaTiO3 provides the oxidation "
            "side and MoS2 provides the "
            "reduction side."
        ),
    ),
    PilotPairDefinition(
        pair_id="PAIR-0004",
        charge_transfer_class=(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        ),
        oxidation_formula="CaTiO3",
        reduction_formula="WS2",
        role_assignment_basis=(
            "Curated Z-scheme mechanism: "
            "CaTiO3 provides the oxidation "
            "side and WS2 provides the "
            "reduction side."
        ),
    ),
]


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
# GET FORMULA
# ---------------------------------------------------------------------------
def get_formula(
    record: MaterialBandRecord,
) -> str:
    return (
        record.formula_normalized
        or record.formula_reported
    )


# ---------------------------------------------------------------------------
# FIND BAND RECORD
# ---------------------------------------------------------------------------
def find_band_record(
    records: list[
        MaterialBandRecord
    ],
    *,
    pair_id: str,
    formula: str,
) -> MaterialBandRecord:
    matches = [
        record
        for record in records
        if (
            record.pair_id
            == pair_id
            and get_formula(
                record
            )
            == formula
        )
    ]

    if len(
        matches
    ) != 1:
        raise ValueError(
            f"Expected exactly one band "
            f"record for {pair_id} / "
            f"{formula}; found "
            f"{len(matches)}."
        )

    return matches[
        0
    ]


# ---------------------------------------------------------------------------
# BUILD ALIGNMENT ID
# ---------------------------------------------------------------------------
def build_alignment_id(
    index: int,
) -> str:
    return (
        f"BALIGN-{index:04d}"
    )


# ---------------------------------------------------------------------------
# BUILD PILOT ALIGNMENTS
# ---------------------------------------------------------------------------
def build_pilot_alignments(
    records: list[
        MaterialBandRecord
    ],
) -> list[
    PairBandAlignmentRecord
]:
    alignments: list[
        PairBandAlignmentRecord
    ] = []

    alignment_index = 1

    for definition in PILOT_PAIR_DEFINITIONS:
        if not is_band_offset_eligible(
            definition.charge_transfer_class
        ):
            continue

        if (
            definition.oxidation_formula
            is None
            or definition.reduction_formula
            is None
            or definition.role_assignment_basis
            is None
        ):
            raise ValueError(
                f"{definition.pair_id}: "
                "eligible pair is missing "
                "explicit OP/RP assignment."
            )

        oxidation_record = (
            find_band_record(
                records,
                pair_id=(
                    definition.pair_id
                ),
                formula=(
                    definition
                    .oxidation_formula
                ),
            )
        )

        reduction_record = (
            find_band_record(
                records,
                pair_id=(
                    definition.pair_id
                ),
                formula=(
                    definition
                    .reduction_formula
                ),
            )
        )

        alignment = (
            build_pair_band_alignment(
                band_alignment_id=(
                    build_alignment_id(
                        alignment_index
                    )
                ),
                oxidation_record=(
                    oxidation_record
                ),
                reduction_record=(
                    reduction_record
                ),
                charge_transfer_class=(
                    definition
                    .charge_transfer_class
                ),
                role_assignment_basis=(
                    definition
                    .role_assignment_basis
                ),
            )
        )

        alignment = (
            alignment.model_copy(
                update={
                    "manual_review_status": (
                        ManualReviewStatus
                        .REVIEWED
                    ),
                }
            )
        )

        alignments.append(
            alignment
        )

        alignment_index += 1

    return alignments


# ---------------------------------------------------------------------------
# VALIDATE ALIGNMENT
# ---------------------------------------------------------------------------
def validate_alignment(
    alignment: PairBandAlignmentRecord,
) -> None:
    expected = (
        alignment.oxidation_cbm_nhe_v
        - alignment.reduction_vbm_nhe_v
    )

    if abs(
        expected
        - alignment
        .mediated_band_difference_nhe_v
    ) > 1e-8:
        raise ValueError(
            f"{alignment.band_alignment_id}: "
            "incorrect mediated band "
            "difference."
        )


# ---------------------------------------------------------------------------
# SAVE ALIGNMENTS
# ---------------------------------------------------------------------------
def save_alignments(
    alignments: list[
        PairBandAlignmentRecord
    ],
) -> None:
    payload = [
        alignment.model_dump(
            mode="json"
        )
        for alignment in alignments
    ]

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# PRINT ALIGNMENT
# ---------------------------------------------------------------------------
def print_alignment(
    alignment: PairBandAlignmentRecord,
) -> None:
    print(
        f"{alignment.pair_id:<10} "
        f"OP={alignment.oxidation_formula:<8} "
        f"RP={alignment.reduction_formula:<6} "
        f"CB(OP)="
        f"{alignment.oxidation_cbm_nhe_v:>8.4f} "
        f"VB(RP)="
        f"{alignment.reduction_vbm_nhe_v:>8.4f} "
        f"offset="
        f"{alignment.mediated_band_difference_nhe_v:>8.4f}"
    )


# ---------------------------------------------------------------------------
# PRINT SKIPPED PAIRS
# ---------------------------------------------------------------------------
def print_skipped_pairs() -> None:
    for definition in PILOT_PAIR_DEFINITIONS:
        if is_band_offset_eligible(
            definition.charge_transfer_class
        ):
            continue

        print(
            f"{definition.pair_id:<10} "
            f"skipped "
            f"({definition.charge_transfer_class.value})"
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

    alignments = (
        build_pilot_alignments(
            records
        )
    )

    if len(
        alignments
    ) != 3:
        raise ValueError(
            "Pilot must produce exactly "
            "3 eligible pair band "
            "alignments."
        )

    for alignment in alignments:
        validate_alignment(
            alignment
        )

    print(
        "PILOT PAIR BAND ALIGNMENTS"
    )
    print(
        "=" * 100
    )

    for alignment in alignments:
        print_alignment(
            alignment
        )

    print()
    print(
        "SKIPPED PAIRS"
    )
    print(
        "-" * 100
    )

    print_skipped_pairs()

    print(
        "-" * 100
    )
    print(
        f"alignments={len(alignments)}"
    )

    save_alignments(
        alignments
    )

    print(
        f"saved={OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()

