import json

from pathlib import Path

from psk_tmd.common.models import (
    ExperimentalSample,
    MechanismAssessment,
)
from psk_tmd.corpus.mechanism_aggregation import (
    aggregate_mechanisms_by_pair,
)


# ---------------------------------------------------------------------------
# LOAD JSON RECORDS
# ---------------------------------------------------------------------------
def load_json_records(
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
    records = load_json_records(
        path
    )

    return [
        ExperimentalSample
        .model_validate(
            record
        )
        for record
        in records
    ]


# ---------------------------------------------------------------------------
# LOAD MECHANISM ASSESSMENTS
# ---------------------------------------------------------------------------
def load_mechanism_assessments(
    path: Path,
) -> list[
    MechanismAssessment
]:
    records = load_json_records(
        path
    )

    return [
        MechanismAssessment
        .model_validate(
            record
        )
        for record
        in records
    ]


# ---------------------------------------------------------------------------
# FORMAT VALUES
# ---------------------------------------------------------------------------
def format_value(
    value,
) -> str:
    if value is None:
        return "-"

    if hasattr(
        value,
        "value",
    ):
        return str(
            value.value
        )

    return str(
        value
    )


# ---------------------------------------------------------------------------
# PRINT SUMMARY
# ---------------------------------------------------------------------------
def print_summary(
    result,
) -> None:
    print()
    print(
        "PAIR-LEVEL MECHANISM "
        "AGGREGATION"
    )
    print(
        "-" * 78
    )

    if not result.pair_results:
        print(
            "No pair-linked mechanism "
            "assessments were found."
        )

    for pair_result in (
        result.pair_results
    ):
        pair_id = (
            pair_result.pair_id
        )

        mechanism = format_value(
            pair_result
            .mechanism_consensus
        )

        ml_class = format_value(
            pair_result
            .charge_transfer_consensus
        )

        disagreement = (
            pair_result
            .has_disagreement
        )

        assessment_count = len(
            pair_result
            .assessment_ids
        )

        print(
            f"{pair_id}"
            f" | mechanism={mechanism}"
            f" | ml_class={ml_class}"
            f" | disagreement={disagreement}"
            f" | assessments={assessment_count}"
        )

    print(
        "-" * 78
    )

    unresolved_count = len(
        result
        .unresolved_assessment_ids
    )

    print(
        "Unresolved assessments: "
        f"{unresolved_count}"
    )

    if (
        result
        .unresolved_assessment_ids
    ):
        print(
            ", ".join(
                result
                .unresolved_assessment_ids
            )
        )

    print()

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    pilot_dir = Path(
        "data/processed/corpus/pilot"
    )

    samples_path = (
        pilot_dir
        / "samples.json"
    )

    assessments_path = (
        pilot_dir
        / "mechanism_assessments.json"
    )

    samples = load_samples(
        samples_path
    )

    assessments = (
        load_mechanism_assessments(
            assessments_path
        )
    )

    result = (
        aggregate_mechanisms_by_pair(
            samples=samples,
            assessments=assessments,
        )
    )

    print_summary(
        result
    )


if __name__ == "__main__":
    main()

