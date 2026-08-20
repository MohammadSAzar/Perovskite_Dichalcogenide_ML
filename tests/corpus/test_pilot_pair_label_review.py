import pytest

from psk_tmd.common.constants import (
    ChargeTransferClass,
    LabelStatus,
    ManualReviewStatus,
    MechanismLabel,
)
from psk_tmd.common.models import (
    PairMechanismLabel,
)

from psk_tmd.corpus.pair_label_review import (
    review_pilot_labels,
)


# ---------------------------------------------------------------------------
# MAKE PILOT LABELS
# ---------------------------------------------------------------------------
def make_pilot_labels(
) -> list[
    PairMechanismLabel
]:
    return [
        PairMechanismLabel(
            pair_id="PAIR-0001",
            source_assessment_ids=[
                "MEA-0001",
            ],
            mechanism_normalized=(
                MechanismLabel.S_SCHEME
            ),
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        ),
        PairMechanismLabel(
            pair_id="PAIR-0002",
            source_assessment_ids=[
                "MEA-0002",
            ],
            mechanism_normalized=(
                MechanismLabel.TYPE_I
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_I
            ),
        ),
        PairMechanismLabel(
            pair_id="PAIR-0003",
            source_assessment_ids=[
                "MEA-0003",
            ],
            mechanism_normalized=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        ),
        PairMechanismLabel(
            pair_id="PAIR-0004",
            source_assessment_ids=[
                "MEA-0004",
            ],
            mechanism_normalized=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        ),
    ]


# ---------------------------------------------------------------------------
# REVIEW ALL PILOT LABELS
# ---------------------------------------------------------------------------
def test_review_all_pilot_labels():
    reviewed = review_pilot_labels(
        make_pilot_labels()
    )

    assert len(
        reviewed
    ) == 4

    for label in reviewed:
        assert (
            label.manual_review_status
            == ManualReviewStatus.REVIEWED
        )

        assert (
            label.label_status
            == LabelStatus.ACCEPTED
        )

        assert (
            label.reviewer_notes
            is not None
        )


# ---------------------------------------------------------------------------
# PILOT REVIEW PRESERVES LABEL VALUES
# ---------------------------------------------------------------------------
def test_pilot_review_preserves_label_values():
    reviewed = review_pilot_labels(
        make_pilot_labels()
    )

    lookup = {
        label.pair_id: label
        for label in reviewed
    }

    assert (
        lookup[
            "PAIR-0001"
        ].mechanism_normalized
        == MechanismLabel.S_SCHEME
    )

    assert (
        lookup[
            "PAIR-0002"
        ].charge_transfer_class
        == ChargeTransferClass.TYPE_I
    )

    assert (
        lookup[
            "PAIR-0003"
        ].charge_transfer_class
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )


# ---------------------------------------------------------------------------
# UNKNOWN PILOT PAIR FAILS
# ---------------------------------------------------------------------------
def test_unknown_pilot_pair_fails():
    labels = make_pilot_labels()

    labels.append(
        PairMechanismLabel(
            pair_id="PAIR-9999",
            mechanism_normalized=(
                MechanismLabel.TYPE_II
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_II
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "No explicit pilot review "
            "decision"
        ),
    ):
        review_pilot_labels(
            labels
        )


# ---------------------------------------------------------------------------
# MISSING PILOT PAIR FAILS
# ---------------------------------------------------------------------------
def test_missing_pilot_pair_fails():
    labels = (
        make_pilot_labels()[
            :-1
        ]
    )

    with pytest.raises(
        ValueError,
        match=(
            "missing from the input labels"
        ),
    ):
        review_pilot_labels(
            labels
        )

