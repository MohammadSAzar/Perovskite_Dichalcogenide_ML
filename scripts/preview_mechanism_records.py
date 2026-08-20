import argparse
import json

from pathlib import Path

from psk_tmd.corpus.builders import (
    build_mechanism_records,
)
from psk_tmd.corpus.extraction import (
    extract_mechanism_candidates,
)
from psk_tmd.corpus.passages import (
    select_relevant_passages,
)
from psk_tmd.corpus.pdf_text import (
    extract_pdf_text,
)
from psk_tmd.corpus.mechanism_postprocess import (
    postprocess_mechanism_extraction,
)


# ---------------------------------------------------------------------------
# MAKE PREVIEW EVIDENCE IDS
# ---------------------------------------------------------------------------
def make_preview_evidence_ids(
    count: int,
) -> list[str]:
    return [
        f"EVD-PREVIEW-{index:04d}"
        for index in range(
            1,
            count + 1,
        )
    ]


# ---------------------------------------------------------------------------
# BUILD JSON PAYLOAD
# ---------------------------------------------------------------------------
def build_json_payload(
    records,
    consistency_result,
) -> dict:
    if consistency_result is None:
        consistency_payload = None

    else:
        consistency_payload = (
            consistency_result.model_dump(
                mode="json"
            )
        )

    return {
        "mechanism_assessment": (
            records.mechanism_assessment.model_dump(
                mode="json"
            )
        ),
        "mechanism_evidence": [
            evidence.model_dump(
                mode="json"
            )
            for evidence
            in records.mechanism_evidence
        ],
        "mechanism_consistency": (
            consistency_payload
        ),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a validated preview of "
            "mechanism-assessment and "
            "mechanism-evidence JSON records "
            "from a paper PDF."
        )
    )

    parser.add_argument(
        "pdf_path",
        type=Path,
        help="Path to the paper PDF.",
    )

    parser.add_argument(
        "--sample-id",
        required=True,
        help=(
            "Experimental sample ID to attach "
            "the mechanism assessment to."
        ),
    )

    parser.add_argument(
        "--series-id",
        default=None,
        help=(
            "Optional sample-series ID that "
            "the mechanism assessment applies to."
        ),
    )

    parser.add_argument(
        "--assessment-id",
        default="MEA-PREVIEW-0001",
        help=(
            "Temporary mechanism-assessment ID "
            "used for this preview."
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
        extract_mechanism_candidates(
            passages
        )
    )

    postprocess_result = (
        postprocess_mechanism_extraction(
            document=document,
            extraction_result=(
                extraction_result
            ),
        )
    )

    extraction_result = (
        postprocess_result
        .extraction_result
    )

    evidence_ids = (
        make_preview_evidence_ids(
            len(
                extraction_result
                .mechanism_evidence_candidates
            )
        )
    )

    records = build_mechanism_records(
        extraction_result=(
            extraction_result
        ),
        mechanism_assessment_id=(
            args.assessment_id
        ),
        evidence_ids=evidence_ids,
        sample_id=args.sample_id,
        applies_to_series_id=(
            args.series_id
        ),
    )

    payload = build_json_payload(
        records=records,
        consistency_result=(
            postprocess_result
            .consistency_result
        ),
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

