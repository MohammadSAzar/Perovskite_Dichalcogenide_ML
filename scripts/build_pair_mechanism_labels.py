import argparse
import json

from pathlib import Path

from psk_tmd.common.models import (
    ExperimentalSample,
    MechanismAssessment,
)
from psk_tmd.corpus.builders import (
    build_pair_mechanism_label,
)
from psk_tmd.corpus.mechanism_aggregation import (
    aggregate_mechanisms_by_pair,
)


# ---------------------------------------------------------------------------
# LOAD JSON LIST
# ---------------------------------------------------------------------------
def load_json_list(
    path: Path,
) -> list[dict]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(
            file
        )

    if not isinstance(
        data,
        list,
    ):
        raise ValueError(
            f"{path} must contain "
            "a JSON list."
        )

    return data


# ---------------------------------------------------------------------------
# LOAD SAMPLES
# ---------------------------------------------------------------------------
def load_samples(
    path: Path,
) -> list[
    ExperimentalSample
]:
    return [
        ExperimentalSample.model_validate(
            record
        )
        for record
        in load_json_list(
            path
        )
    ]


# ---------------------------------------------------------------------------
# LOAD MECHANISM ASSESSMENTS
# ---------------------------------------------------------------------------
def load_mechanism_assessments(
    path: Path,
) -> list[
    MechanismAssessment
]:
    return [
        MechanismAssessment.model_validate(
            record
        )
        for record
        in load_json_list(
            path
        )
    ]


# ---------------------------------------------------------------------------
# WRITE JSON LIST
# ---------------------------------------------------------------------------
def write_json_list(
    path: Path,
    records: list[dict],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            records,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write(
            "\n"
        )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build pending pair-level "
            "mechanism labels from curated "
            "sample-level assessments."
        )
    )

    parser.add_argument(
        "--samples",
        type=Path,
        required=True,
        help=(
            "Path to samples.json."
        ),
    )

    parser.add_argument(
        "--assessments",
        type=Path,
        required=True,
        help=(
            "Path to "
            "mechanism_assessments.json."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help=(
            "Output path for pair-level "
            "mechanism labels."
        ),
    )

    args = parser.parse_args()

    samples = load_samples(
        args.samples
    )

    assessments = (
        load_mechanism_assessments(
            args.assessments
        )
    )

    linkage_result = (
        aggregate_mechanisms_by_pair(
            samples=samples,
            assessments=assessments,
        )
    )

    if (
        linkage_result
        .unresolved_assessment_ids
    ):
        unresolved = ", ".join(
            linkage_result
            .unresolved_assessment_ids
        )

        raise ValueError(
            "Cannot build pair-level "
            "labels because some mechanism "
            "assessments could not be "
            f"linked to a pair: {unresolved}"
        )

    labels = [
        build_pair_mechanism_label(
            pair_result
        )
        for pair_result
        in linkage_result.pair_results
    ]

    records = [
        label.model_dump(
            mode="json"
        )
        for label
        in labels
    ]

    write_json_list(
        path=args.output,
        records=records,
    )

    print(
        f"Wrote {len(records)} "
        f"pair-level mechanism labels "
        f"to {args.output}"
    )


if __name__ == "__main__":
    main()

