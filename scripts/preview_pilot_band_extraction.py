from dataclasses import dataclass
from pathlib import Path

from psk_tmd.common.config import (
    PROJECT_ROOT,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_structured_extraction import (
    StructuredBandValue,
    extract_structured_band_values,
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
    path: Path
    pair: PairRecord


# ---------------------------------------------------------------------------
# PILOT PAPERS
# ---------------------------------------------------------------------------
PILOT_PAPERS = [
    PilotPaper(
        name="Mao 2019",
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
# FORMAT OPTIONAL ENUM
# ---------------------------------------------------------------------------
def format_optional_enum(
    value: object | None,
) -> str:
    if value is None:
        return "-"

    enum_value = getattr(
        value,
        "value",
        None,
    )

    if enum_value is not None:
        return str(
            enum_value
        )

    return str(
        value
    )


# ---------------------------------------------------------------------------
# CLEAN PREVIEW TEXT
# ---------------------------------------------------------------------------
def clean_preview_text(
    text: str,
    *,
    max_length: int = 150,
) -> str:
    clean = " ".join(
        text.split()
    )

    if len(
        clean
    ) <= max_length:
        return clean

    return (
        clean[
            :max_length - 3
        ]
        + "..."
    )


# ---------------------------------------------------------------------------
# PRINT VALUE
# ---------------------------------------------------------------------------
def print_value(
    *,
    paper: PilotPaper,
    value: StructuredBandValue,
) -> None:
    print(
        f"{paper.name:<12} | "
        f"{value.formula:<10} | "
        f"{value.property_type.value:<10} | "
        f"{value.numeric_value:>7.3f} | "
        f"{format_optional_enum(value.reference_scale):<8} | "
        f"{format_optional_enum(value.band_gap_type):<8} | "
        f"{value.claim_context.value:<16} | "
        f"{value.extraction_basis}"
    )

    print(
        f"    {clean_preview_text(value.source_text)}"
    )


# ---------------------------------------------------------------------------
# PRINT PAPER SUMMARY
# ---------------------------------------------------------------------------
def print_paper_summary(
    *,
    paper: PilotPaper,
    values: list[
        StructuredBandValue
    ],
) -> None:
    band_gaps = sum(
        value.property_type.value
        == "band_gap"
        for value in values
    )

    cbm = sum(
        value.property_type.value
        == "cbm"
        for value in values
    )

    vbm = sum(
        value.property_type.value
        == "vbm"
        for value in values
    )

    print(
        f"{paper.name:<12}"
        f" total={len(values):<3}"
        f" Eg={band_gaps:<3}"
        f" CB={cbm:<3}"
        f" VB={vbm:<3}"
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    results: list[
        tuple[
            PilotPaper,
            list[
                StructuredBandValue
            ],
        ]
    ] = []

    print(
        "PILOT STRUCTURED BAND EXTRACTION"
    )
    print(
        "=" * 110
    )

    for paper in PILOT_PAPERS:
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

        results.append(
            (
                paper,
                values,
            )
        )

        print_paper_summary(
            paper=paper,
            values=values,
        )

    print()
    print(
        "EXTRACTED VALUES"
    )
    print(
        "=" * 110
    )
    print(
        "PAPER        | MATERIAL   | PROPERTY   |   VALUE | "
        "SCALE    | GAP TYPE | CONTEXT          | BASIS"
    )
    print(
        "-" * 110
    )

    for (
        paper,
        values,
    ) in results:
        for value in values:
            print_value(
                paper=paper,
                value=value,
            )


if __name__ == "__main__":
    main()


