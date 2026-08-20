import json

from pathlib import Path

from psk_tmd.common.models import PairMechanismLabel
from psk_tmd.corpus.pair_label_review import accept_pair_mechanism_label
from psk_tmd.corpus.pair_label_review import (
    review_pilot_labels,
)

# ---------------------------------------------------------------------------
# PILOT REVIEW NOTES
# ---------------------------------------------------------------------------
PILOT_REVIEW_NOTES = {
    "PAIR-0001": (
        "Curated pilot review confirms "
        "S-scheme mechanism and "
        "mediated-recombination ML class."
    ),
    "PAIR-0002": (
        "Curated pilot review confirms "
        "Type-I mechanism and Type-I "
        "ML class."
    ),
    "PAIR-0003": (
        "Curated pilot review confirms "
        "Z-scheme mechanism and "
        "mediated-recombination ML class."
    ),
    "PAIR-0004": (
        "Curated pilot review confirms "
        "Z-scheme mechanism and "
        "mediated-recombination ML class."
    ),
}


# ---------------------------------------------------------------------------
# LOAD PAIR LABELS
# ---------------------------------------------------------------------------
def load_pair_labels(
    path: Path,
) -> list[
    PairMechanismLabel
]:
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

    return [
        PairMechanismLabel.model_validate(
            record
        )
        for record in data
    ]


# ---------------------------------------------------------------------------
# REVIEW PILOT LABELS
# ---------------------------------------------------------------------------
def review_pilot_labels(
    labels: list[
        PairMechanismLabel
    ],
) -> list[
    PairMechanismLabel
]:
    reviewed_labels: list[
        PairMechanismLabel
    ] = []

    seen_pair_ids: set[str] = set()

    for label in labels:
        pair_id = label.pair_id

        if pair_id not in (
            PILOT_REVIEW_NOTES
        ):
            raise ValueError(
                "No explicit pilot review "
                f"decision for {pair_id}."
            )

        reviewed = (
            accept_pair_mechanism_label(
                label=label,
                reviewer_notes=(
                    PILOT_REVIEW_NOTES[
                        pair_id
                    ]
                ),
            )
        )

        reviewed_labels.append(
            reviewed
        )

        seen_pair_ids.add(
            pair_id
        )

    missing_pair_ids = (
        set(
            PILOT_REVIEW_NOTES
        )
        - seen_pair_ids
    )

    if missing_pair_ids:
        missing = ", ".join(
            sorted(
                missing_pair_ids
            )
        )

        raise ValueError(
            "Pilot review decisions exist "
            "for pair IDs missing from "
            f"the input labels: {missing}"
        )

    return reviewed_labels


# ---------------------------------------------------------------------------
# WRITE PAIR LABELS
# ---------------------------------------------------------------------------
def write_pair_labels(
    path: Path,
    labels: list[
        PairMechanismLabel
    ],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    records = [
        label.model_dump(
            mode="json"
        )
        for label in labels
    ]

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
    input_path = Path(
        "data/interim/corpus/"
        "pilot_v0_3/"
        "pair_mechanism_labels.json"
    )

    output_path = Path(
        "data/interim/corpus/"
        "pilot_v0_3/"
        "pair_mechanism_labels_reviewed.json"
    )

    labels = load_pair_labels(
        input_path
    )

    reviewed_labels = (
        review_pilot_labels(
            labels
        )
    )

    write_pair_labels(
        path=output_path,
        labels=reviewed_labels,
    )

    print(
        f"Wrote {len(reviewed_labels)} "
        "reviewed pair-level labels to "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()


