import argparse
import json

from pathlib import Path

from psk_tmd.corpus.builders import build_pair_record
from psk_tmd.corpus.pair_extraction import extract_pair_candidates
from psk_tmd.corpus.passages import select_relevant_passages
from psk_tmd.corpus.pdf_text import extract_pdf_text


# ---------------------------------------------------------------------------
# BUILD JSON PAYLOAD
# ---------------------------------------------------------------------------
def build_json_payload(
    extraction_result,
    pair_record,
) -> dict:
    if (
        extraction_result
        .primary_pair_candidate
        is None
    ):
        primary_pair_payload = None

    else:
        primary_pair_payload = (
            extraction_result
            .primary_pair_candidate
            .model_dump(
                mode="json"
            )
        )

    if pair_record is None:
        pair_record_payload = None

    else:
        pair_record_payload = (
            pair_record.model_dump(
                mode="json"
            )
        )

    return {
        "primary_pair_candidate": (
            primary_pair_payload
        ),
        "pair_record": (
            pair_record_payload
        ),
        "pair_candidates": [
            candidate.model_dump(
                mode="json"
            )
            for candidate
            in extraction_result
            .pair_candidates
        ],
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a validated preview "
            "of PSK-TMD pair extraction "
            "from a paper PDF."
        )
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the paper PDF.",
    )

    parser.add_argument(
        "--pair-id",
        default="PAIR-PREVIEW-0001",
        help=(
            "Temporary pair ID used "
            "for this preview."
        ),
    )

    args = parser.parse_args()

    document = extract_pdf_text(
        args.pdf_path
    )

    passages = select_relevant_passages(
        document
    )

    extraction_result = (
        extract_pair_candidates(
            passages
        )
    )

    pair_record = build_pair_record(
        extraction_result=(
            extraction_result
        ),
        pair_id=args.pair_id,
    )

    payload = build_json_payload(
        extraction_result=(
            extraction_result
        ),
        pair_record=pair_record,
    )

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

