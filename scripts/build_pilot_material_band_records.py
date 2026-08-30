import json

from dataclasses import dataclass
from pathlib import Path

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.common.models import (
    MaterialBandRecord,
    PairRecord,
)
from psk_tmd.corpus.band_structured_extraction import (
    extract_structured_band_values,
)
from psk_tmd.corpus.material_band_record_builder import (
    build_pair_material_band_records,
)
from psk_tmd.corpus.pdf_text import (
    extract_pdf_text,
)


# ---------------------------------------------------------------------------
# PILOT PAPER
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilotPaper:
    name: str
    paper_id: str
    path: Path
    pair: PairRecord


# ---------------------------------------------------------------------------
# PILOT PAPER IDS
# ---------------------------------------------------------------------------
PAPER_ID_MAO = "PPR-0002"
PAPER_ID_JIANG = "PPR-0003"
PAPER_ID_RASHKI = "PPR-0004"
PAPER_ID_QIN = "PPR-0001"


# ---------------------------------------------------------------------------
# PILOT PAPERS
# ---------------------------------------------------------------------------
PILOT_PAPERS = [
    PilotPaper(
        name="Mao 2019",
        paper_id=PAPER_ID_MAO,
        path=(
            PROJECT_ROOT
            / "data"
            / "raw"
            / "literature"
            / "2019.Mao.pdf"
        ),
        pair=PairRecord(
            pair_id="PAIR-0002",
            psk_formula_reported="LaNiO3",
            psk_formula_normalized="LaNiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        ),
    ),
    PilotPaper(
        name="Jiang 2020",
        paper_id=PAPER_ID_JIANG,
        path=(
            PROJECT_ROOT
            / "data"
            / "raw"
            / "literature"
            / "2020.Jiang.pdf"
        ),
        pair=PairRecord(
            pair_id="PAIR-0003",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        ),
    ),
    PilotPaper(
        name="Rashki 2022",
        paper_id=PAPER_ID_RASHKI,
        path=(
            PROJECT_ROOT
            / "data"
            / "raw"
            / "literature"
            / "2022.Rashki.pdf"
        ),
        pair=PairRecord(
            pair_id="PAIR-0004",
            psk_formula_reported="CaTiO3",
            psk_formula_normalized="CaTiO3",
            tmd_formula_reported="WS2",
            tmd_formula_normalized="WS2",
        ),
    ),
    PilotPaper(
        name="Qin 2023",
        paper_id=PAPER_ID_QIN,
        path=(
            PROJECT_ROOT
            / "data"
            / "raw"
            / "literature"
            / "2023.Qin.pdf"
        ),
        pair=PairRecord(
            pair_id="PAIR-0001",
            psk_formula_reported="PbTiO3",
            psk_formula_normalized="PbTiO3",
            tmd_formula_reported="MoS2",
            tmd_formula_normalized="MoS2",
        ),
    ),
]


# ---------------------------------------------------------------------------
# OUTPUT PATH
# ---------------------------------------------------------------------------
OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "interim"
    / "corpus"
    / "pilot_v0_3"
    / "material_band_records.json"
)


# ---------------------------------------------------------------------------
# BUILD RECORD IDS
# ---------------------------------------------------------------------------
def build_record_ids(
    paper_index: int,
) -> tuple[
    str,
    str,
]:
    psk_id = (
        f"BAND-{paper_index:04d}-PSK"
    )

    tmd_id = (
        f"BAND-{paper_index:04d}-TMD"
    )

    return (
        psk_id,
        tmd_id,
    )


# ---------------------------------------------------------------------------
# BUILD PAPER RECORDS
# ---------------------------------------------------------------------------
def build_paper_records(
    paper: PilotPaper,
    *,
    paper_index: int,
) -> list[
    MaterialBandRecord
]:
    document = (
        extract_pdf_text(
            paper.path
        )
    )

    values = (
        extract_structured_band_values(
            document.full_text,
            pair=paper.pair,
        )
    )

    psk_id, tmd_id = (
        build_record_ids(
            paper_index
        )
    )

    return (
        build_pair_material_band_records(
            paper_id=paper.paper_id,
            pair=paper.pair,
            values=values,
            psk_band_record_id=psk_id,
            tmd_band_record_id=tmd_id,
            source_location=(
                paper.path.name
            ),
        )
    )


# ---------------------------------------------------------------------------
# VALIDATE PILOT RECORD
# ---------------------------------------------------------------------------
def validate_pilot_record(
    record: MaterialBandRecord,
) -> None:
    if (
        record.reported_band_gap_ev
        is None
    ):
        raise ValueError(
            f"{record.band_record_id}: "
            "missing reported band gap."
        )

    if record.reported_cbm is None:
        raise ValueError(
            f"{record.band_record_id}: "
            "missing reported CBM."
        )

    if record.reported_vbm is None:
        raise ValueError(
            f"{record.band_record_id}: "
            "missing reported VBM."
        )


# ---------------------------------------------------------------------------
# BUILD PILOT RECORDS
# ---------------------------------------------------------------------------
def build_pilot_records() -> list[
    MaterialBandRecord
]:
    records: list[
        MaterialBandRecord
    ] = []

    for (
        paper_index,
        paper,
    ) in enumerate(
        PILOT_PAPERS,
        start=1,
    ):
        paper_records = (
            build_paper_records(
                paper,
                paper_index=paper_index,
            )
        )

        for record in paper_records:
            validate_pilot_record(
                record
            )

        records.extend(
            paper_records
        )

    return records


# ---------------------------------------------------------------------------
# PRINT RECORD
# ---------------------------------------------------------------------------
def print_record(
    record: MaterialBandRecord,
) -> None:
    print(
        f"{record.paper_id:<18} "
        f"{record.pair_id:<10} "
        f"{record.material_type.value:<4} "
        f"{record.formula_reported:<10} "
        f"Eg={record.reported_band_gap_ev:<5.2f} "
        f"CB={record.reported_cbm:<6.2f} "
        f"VB={record.reported_vbm:<5.2f} "
        f"scale="
        f"{record.reported_reference_scale.value:<8} "
        f"gap_type="
        f"{record.band_gap_type.value:<8} "
        f"context="
        f"{record.claim_context.value}"
    )


# ---------------------------------------------------------------------------
# SAVE RECORDS
# ---------------------------------------------------------------------------
def save_records(
    records: list[
        MaterialBandRecord
    ],
) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = [
        record.model_dump(
            mode="json"
        )
        for record in records
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
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        build_pilot_records()
    )

    print(
        "PILOT MATERIAL BAND RECORDS"
    )
    print(
        "=" * 120
    )

    for record in records:
        print_record(
            record
        )

    print(
        "-" * 120
    )
    print(
        f"records={len(records)}"
    )

    if len(records) != 8:
        raise ValueError(
            "Pilot must produce exactly "
            "8 MaterialBandRecord objects."
        )

    save_records(
        records
    )

    print(
        f"saved={OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()

