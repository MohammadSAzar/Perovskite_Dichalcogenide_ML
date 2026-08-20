import argparse

from pathlib import Path

from psk_tmd.corpus.extraction import (
    extract_mechanism_candidates,
)
from psk_tmd.corpus.passages import (
    select_relevant_passages,
)
from psk_tmd.corpus.pdf_text import (
    extract_pdf_text,
)


# ---------------------------------------------------------------------------
# SHORTEN TEXT
# ---------------------------------------------------------------------------
def shorten_text(
    text: str,
    max_length: int = 260,
) -> str:
    if len(text) <= max_length:
        return text

    return (
        text[:max_length].rstrip()
        + "..."
    )


# ---------------------------------------------------------------------------
# PRINT MECHANISM CLAIMS
# ---------------------------------------------------------------------------
def print_mechanism_claims(
    result,
) -> None:
    print(
        "\n=== MECHANISM CLAIM ==="
    )

    if not result.mechanism_claims:
        print(
            "No mechanism claim found."
        )

        return

    for candidate in (
        result.mechanism_claims
    ):
        print(
            "Normalized:",
            candidate.mechanism_normalized.value,
        )

        print(
            "Reported:",
            candidate.mechanism_reported,
        )

        print(
            "ML class:",
            candidate.charge_transfer_class,
        )

        print(
            "Page:",
            candidate.page_number,
        )

        print(
            "Section:",
            candidate.section_role.value,
        )

        print(
            "Section title:",
            candidate.section_title,
        )

        print(
            "Score:",
            f"{candidate.score:.2f}",
        )

        print(
            "Source:",
            shorten_text(
                candidate.source_text
            ),
        )


# ---------------------------------------------------------------------------
# PRINT CHARACTERIZATION SUMMARY
# ---------------------------------------------------------------------------
def print_characterization_summary(
    result,
) -> None:
    print(
        "\n=== CHARACTERIZATION SUMMARY ==="
    )

    if not (
        result.characterization_candidates
    ):
        print(
            "No characterization "
            "candidates found."
        )

        return

    for candidate in (
        result.characterization_candidates
    ):
        context = ", ".join(
            item.value
            for item
            in candidate.required_context
        )

        if not context:
            context = "-"

        print(
            f"{candidate.evidence_type} | "
            f"role="
            f"{candidate.characterization_role.value} | "
            f"discriminating="
            f"{candidate.mechanism_discriminating} | "
            f"requires_context="
            f"{candidate.requires_context} | "
            f"context={context} | "
            f"page="
            f"{candidate.page_number} | "
            f"section="
            f"{candidate.section_role.value}"
        )


# ---------------------------------------------------------------------------
# PRINT MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def print_mechanism_evidence(
    result,
) -> None:
    print(
        "\n=== MECHANISM EVIDENCE CANDIDATES ==="
    )

    if not (
        result.mechanism_evidence_candidates
    ):
        print(
            "No mechanism evidence "
            "candidates found."
        )

        return

    for candidate in (
        result.mechanism_evidence_candidates
    ):
        print(
            f"\n{candidate.evidence_type}"
        )

        print(
            "Role:",
            candidate.characterization_role.value,
        )

        print(
            "Mechanism discriminating:",
            candidate.mechanism_discriminating,
        )

        print(
            "Requires context:",
            candidate.requires_context,
        )

        context = ", ".join(
            item.value
            for item
            in candidate.required_context
        )

        if not context:
            context = "-"

        print(
            "Required context:",
            context,
        )

        print(
            "Page:",
            candidate.page_number,
        )

        print(
            "Section:",
            candidate.section_role.value,
        )

        print(
            "Section title:",
            candidate.section_title,
        )

        print(
            "Score:",
            f"{candidate.score:.2f}",
        )

        print(
            "Matched:",
            ", ".join(
                candidate.matched_terms
            ),
        )

        print(
            "Source:",
            shorten_text(
                candidate.source_text
            ),
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect scientific-role-aware "
            "mechanism extraction from a PDF."
        )
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the paper PDF.",
    )

    args = parser.parse_args()

    document = extract_pdf_text(
        args.pdf_path
    )

    passages = select_relevant_passages(
        document
    )

    result = (
        extract_mechanism_candidates(
            passages
        )
    )

    print(
        "\n=== DOCUMENT ==="
    )

    print(
        f"PDF: {args.pdf_path}"
    )

    print(
        f"Pages: {document.page_count}"
    )

    print_mechanism_claims(
        result
    )

    print_characterization_summary(
        result
    )

    print_mechanism_evidence(
        result
    )

    print(
        "\nMechanism extraction "
        "inspection completed."
    )


if __name__ == "__main__":
    main()


