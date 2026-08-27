from pathlib import Path

from psk_tmd.corpus.electronegativity_qc import (
    compare_electronegativity_references,
    get_flagged_comparisons,
    load_electronegativity_reference,
)


# ---------------------------------------------------------------------------
# REFERENCE PATHS
# ---------------------------------------------------------------------------
CARDENAS_PATH = Path(
    "data/external/"
    "electronegativity/"
    "cardenas2016_absolute_"
    "electronegativity.json"
)

PUBCHEM_PATH = Path(
    "data/external/"
    "electronegativity/"
    "pubchem_absolute_"
    "electronegativity.json"
)

QC_THRESHOLD_EV = 0.25


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    canonical_records = (
        load_electronegativity_reference(
            CARDENAS_PATH
        )
    )

    validation_records = (
        load_electronegativity_reference(
            PUBCHEM_PATH
        )
    )

    comparisons = (
        compare_electronegativity_references(
            canonical_records=(
                canonical_records
            ),
            validation_records=(
                validation_records
            ),
            discrepancy_threshold_ev=(
                QC_THRESHOLD_EV
            ),
        )
    )

    flagged = (
        get_flagged_comparisons(
            comparisons
        )
    )

    print(
        "ELECTRONEGATIVITY "
        "REFERENCE QC"
    )
    print(
        "-" * 70
    )

    print(
        "Canonical: "
        "Cardenas et al. 2016"
    )

    print(
        "Validation: "
        "PubChem IE + EA"
    )

    print(
        "Comparable elements: "
        f"{len(comparisons)}"
    )

    print(
        "QC threshold: "
        f"{QC_THRESHOLD_EV:.2f} eV"
    )

    print(
        "Flagged discrepancies: "
        f"{len(flagged)}"
    )

    if not flagged:
        return

    print()
    print(
        "FLAGGED ELEMENTS"
    )
    print(
        "-" * 70
    )

    for comparison in sorted(
        flagged,
        key=lambda item: (
            item.absolute_delta_ev
        ),
        reverse=True,
    ):
        print(
            f"{comparison.element_symbol:>3}  "
            f"Cardenas="
            f"{comparison.canonical_ev:.4f}  "
            f"PubChem="
            f"{comparison.validation_ev:.4f}  "
            f"delta="
            f"{comparison.delta_ev:+.4f}"
        )


if __name__ == "__main__":
    main()

