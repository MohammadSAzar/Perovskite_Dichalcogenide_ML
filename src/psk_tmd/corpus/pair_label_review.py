from psk_tmd.common.constants import (
    ChargeTransferClass,
    LabelStatus,
    ManualReviewStatus,
    MechanismLabel,
)
from psk_tmd.common.models import (
    PairMechanismLabel,
)


# ---------------------------------------------------------------------------
# ACCEPT PAIR MECHANISM LABEL
# ---------------------------------------------------------------------------
def accept_pair_mechanism_label(
    label: PairMechanismLabel,
    mechanism_normalized: (
        MechanismLabel | None
    ) = None,
    charge_transfer_class: (
        ChargeTransferClass | None
    ) = None,
    reviewer_notes: str | None = None,
) -> PairMechanismLabel:
    mechanism = (
        mechanism_normalized
        if mechanism_normalized
        is not None
        else label.mechanism_normalized
    )

    charge_class = (
        charge_transfer_class
        if charge_transfer_class
        is not None
        else label.charge_transfer_class
    )

    if mechanism is None:
        raise ValueError(
            "An accepted pair label must "
            "have a resolved mechanism."
        )

    if charge_class is None:
        raise ValueError(
            "An accepted pair label must "
            "have a resolved "
            "charge-transfer class."
        )

    return label.model_copy(
        update={
            "mechanism_normalized": (
                mechanism
            ),
            "charge_transfer_class": (
                charge_class
            ),
            "has_disagreement": False,
            "manual_review_status": (
                ManualReviewStatus.REVIEWED
            ),
            "label_status": (
                LabelStatus.ACCEPTED
            ),
            "reviewer_notes": (
                reviewer_notes
            ),
        }
    )


# ---------------------------------------------------------------------------
# MARK PAIR MECHANISM LABEL UNCERTAIN
# ---------------------------------------------------------------------------
def mark_pair_mechanism_label_uncertain(
    label: PairMechanismLabel,
    reviewer_notes: str | None = None,
) -> PairMechanismLabel:
    return label.model_copy(
        update={
            "manual_review_status": (
                ManualReviewStatus.REVIEWED
            ),
            "label_status": (
                LabelStatus.UNCERTAIN
            ),
            "reviewer_notes": (
                reviewer_notes
            ),
        }
    )


# ---------------------------------------------------------------------------
# EXCLUDE PAIR MECHANISM LABEL
# ---------------------------------------------------------------------------
def exclude_pair_mechanism_label(
    label: PairMechanismLabel,
    reviewer_notes: str,
) -> PairMechanismLabel:
    if not reviewer_notes.strip():
        raise ValueError(
            "An excluded pair label "
            "requires reviewer notes."
        )

    return label.model_copy(
        update={
            "manual_review_status": (
                ManualReviewStatus.REVIEWED
            ),
            "label_status": (
                LabelStatus.EXCLUDED
            ),
            "reviewer_notes": (
                reviewer_notes
            ),
        }
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
# REVIEW PILOT PAIR LABELS
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

