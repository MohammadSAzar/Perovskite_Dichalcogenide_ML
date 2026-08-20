import re
import argparse
import json

from collections import Counter
from pathlib import Path

from psk_tmd.corpus.passages import (
    PassageCategory,
    RelevantPassage,
    select_relevant_passages,
)
from psk_tmd.corpus.pdf_text import extract_pdf_text


# ---------------------------------------------------------------------------
# LOAD JSON
# ---------------------------------------------------------------------------
def load_json(
    path: Path,
) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"JSON file does not exist: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(
            file
        )

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a JSON list in: {path}"
        )

    return data


# ---------------------------------------------------------------------------
# FIND PAPER ASSESSMENTS
# ---------------------------------------------------------------------------
def find_paper_assessments(
    paper_id: str,
    pilot_dir: Path,
) -> list[dict]:
    samples = load_json(
        pilot_dir / "samples.json"
    )

    assessments = load_json(
        pilot_dir
        / "mechanism_assessments.json"
    )

    sample_ids = {
        sample["sample_id"]
        for sample in samples
        if sample["paper_id"] == paper_id
    }

    return [
        assessment
        for assessment in assessments
        if assessment["sample_id"] in sample_ids
    ]


# ---------------------------------------------------------------------------
# FIND ASSESSMENT EVIDENCE
# ---------------------------------------------------------------------------
def find_assessment_evidence(
    assessment_ids: set[str],
    pilot_dir: Path,
) -> list[dict]:
    evidence_records = load_json(
        pilot_dir
        / "mechanism_evidence.json"
    )

    return [
        evidence
        for evidence in evidence_records
        if (
            evidence[
                "mechanism_assessment_id"
            ]
            in assessment_ids
        )
    ]


# ---------------------------------------------------------------------------
# PRINT DOCUMENT SUMMARY
# ---------------------------------------------------------------------------
def print_document_summary(
    pdf_path: Path,
    page_count: int,
    passages: list[RelevantPassage],
) -> None:
    category_counts = Counter(
        passage.category.value
        for passage in passages
    )

    print(
        "\n=== DOCUMENT ==="
    )

    print(
        f"PDF: {pdf_path}"
    )

    print(
        f"Pages: {page_count}"
    )

    print(
        "Selected passage records: "
        f"{len(passages)}"
    )

    print(
        "\n=== PASSAGE COUNTS ==="
    )

    for category in PassageCategory:
        print(
            f"{category.value}: "
            f"{category_counts[category.value]}"
        )


# ---------------------------------------------------------------------------
# PRINT CURATED ASSESSMENT
# ---------------------------------------------------------------------------
def print_curated_assessments(
    assessments: list[dict],
) -> None:
    print(
        "\n=== CURATED MECHANISM ASSESSMENT ==="
    )

    if not assessments:
        print(
            "No curated assessment found."
        )
        return

    for assessment in assessments:
        print(
            "Assessment:",
            assessment[
                "mechanism_assessment_id"
            ],
        )

        print(
            "Sample:",
            assessment[
                "sample_id"
            ],
        )

        print(
            "Series:",
            assessment.get(
                "applies_to_series_id"
            ),
        )

        print(
            "Reported:",
            assessment.get(
                "mechanism_reported"
            ),
        )

        print(
            "Normalized:",
            assessment.get(
                "mechanism_normalized"
            ),
        )

        print(
            "ML class:",
            assessment.get(
                "charge_transfer_class"
            ),
        )

        print(
            "Explicit:",
            assessment.get(
                "claim_explicit"
            ),
        )

        print(
            "Confidence:",
            assessment.get(
                "assessment_confidence"
            ),
        )

        print()


# ---------------------------------------------------------------------------
# PRINT CURATED EVIDENCE
# ---------------------------------------------------------------------------
def print_curated_evidence(
    evidence_records: list[dict],
) -> None:
    print(
        "\n=== CURATED MECHANISM EVIDENCE ==="
    )

    if not evidence_records:
        print(
            "No curated evidence found."
        )
        return

    for evidence in evidence_records:
        print(
            f"{evidence['evidence_id']} | "
            f"{evidence['evidence_type']} | "
            f"{evidence['support']} | "
            f"{evidence['evidence_strength']}"
        )

        print(
            "Subtype:",
            evidence.get(
                "evidence_subtype"
            ),
        )

        print(
            "Source:",
            evidence.get(
                "source_location"
            ),
        )

        print(
            "Result:",
            evidence.get(
                "reported_result"
            ),
        )

        print(
            "Notes:",
            evidence.get(
                "notes"
            ),
        )

        print()


# ---------------------------------------------------------------------------
# PRINT MECHANISM PASSAGES
# ---------------------------------------------------------------------------
def print_mechanism_passages(
    passages: list[RelevantPassage],
) -> None:
    mechanism_passages = [
        passage
        for passage in passages
        if (
            passage.category
            == PassageCategory.MECHANISM
        )
    ]

    print(
        "\n=== AUTOMATIC MECHANISM PASSAGES ==="
    )

    if not mechanism_passages:
        print(
            "No mechanism passages were selected."
        )
        return

    for passage in mechanism_passages:
        print(
            f"{passage.passage_id} | "
            f"page {passage.page_number}"
        )

        print(
            "Matched:",
            ", ".join(
                passage.matched_terms
            ),
        )

        print(
            "Text:",
            passage.text,
        )

        print()


# ---------------------------------------------------------------------------
# PRINT OTHER CATEGORY EXAMPLES
# ---------------------------------------------------------------------------
def print_category_examples(
    passages: list[RelevantPassage],
    category: PassageCategory,
    limit: int = 5,
) -> None:
    selected = [
        passage
        for passage in passages
        if passage.category == category
    ]

    print(
        f"\n=== {category.value.upper()} "
        f"EXAMPLES ==="
    )

    if not selected:
        print(
            "No passages selected."
        )
        return

    for passage in selected[:limit]:
        if passage.page_number is not None:
            location = (
                f"page {passage.page_number}"
            )

        else:
            location = (
                passage.section_title
                or "unknown location"
            )

        print(
            f"{passage.passage_id} | "
            f"{location}"
        )

        print(
            "Matched:",
            ", ".join(
                passage.matched_terms
            ),
        )

        print(
            "Text:",
            passage.text,
        )

        print()


# ---------------------------------------------------------------------------
# COUNT WORDS
# ---------------------------------------------------------------------------
def count_words(
    text: str,
) -> int:
    return len(
        re.findall(
            r"\b[\w'-]+\b",
            text,
        )
    )


# ---------------------------------------------------------------------------
# PRINT TEXT REDUCTION SUMMARY
# ---------------------------------------------------------------------------
def print_text_reduction_summary(
    full_text: str,
    passages: list[RelevantPassage],
) -> None:
    full_word_count = count_words(
        full_text
    )

    all_selected_word_count = sum(
        count_words(
            passage.text
        )
        for passage in passages
    )

    unique_texts = {
        (
            passage.page_number,
            passage.text,
        )
        for passage in passages
    }

    unique_selected_word_count = sum(
        count_words(text)
        for _, text in unique_texts
    )

    print(
        "\n=== TEXT REDUCTION ==="
    )

    print(
        f"Full document words: "
        f"{full_word_count}"
    )

    print(
        f"Passage words with category duplication: "
        f"{all_selected_word_count}"
    )

    print(
        f"Unique selected words: "
        f"{unique_selected_word_count}"
    )

    print(
        f"Unique selected chunks: "
        f"{len(unique_texts)}"
    )

    if full_word_count > 0:
        selected_fraction = (
            unique_selected_word_count
            / full_word_count
        )

        print(
            "Unique selected fraction: "
            f"{selected_fraction:.1%}"
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect automatic passage selection "
            "against curated pilot evidence."
        )
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the pilot paper PDF.",
    )

    parser.add_argument(
        "--paper-id",
        required=True,
        help=(
            "Pilot paper ID, "
            "for example PPR-0003."
        ),
    )

    parser.add_argument(
        "--pilot-dir",
        type=Path,
        default=Path(
            "data/processed/corpus/pilot"
        ),
        help=(
            "Directory containing the "
            "current v0.2 pilot JSON tables."
        ),
    )

    args = parser.parse_args()

    print(
        "\n=== PILOT DIRECTORY ==="
    )

    print(
        args.pilot_dir.resolve()
    )

    document = extract_pdf_text(
        args.pdf_path
    )

    passages = (
        select_relevant_passages(
            document
        )
    )

    assessments = (
        find_paper_assessments(
            paper_id=args.paper_id,
            pilot_dir=args.pilot_dir,
        )
    )

    assessment_ids = {
        assessment[
            "mechanism_assessment_id"
        ]
        for assessment in assessments
    }

    evidence_records = (
        find_assessment_evidence(
            assessment_ids=assessment_ids,
            pilot_dir=args.pilot_dir,
        )
    )

    print_document_summary(
        pdf_path=args.pdf_path,
        page_count=document.page_count,
        passages=passages,
    )

    print_text_reduction_summary(
        full_text=document.full_text,
        passages=passages,
    )

    print_curated_assessments(
        assessments
    )

    print_curated_evidence(
        evidence_records
    )

    print_mechanism_passages(
        passages
    )

    print_category_examples(
        passages,
        PassageCategory.MATERIAL,
    )

    print_category_examples(
        passages,
        PassageCategory.PHOTOCATALYTIC_TEST,
    )

    print_category_examples(
        passages,
        PassageCategory.SYNTHESIS,
    )

    print(
        "\nPilot passage inspection completed."
    )


if __name__ == "__main__":
    main()

