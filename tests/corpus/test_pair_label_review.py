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
    accept_pair_mechanism_label,
    exclude_pair_mechanism_label,
    mark_pair_mechanism_label_uncertain,
)


# ---------------------------------------------------------------------------
# MAKE PENDING LABEL
# ---------------------------------------------------------------------------
def make_pending_label(
) -> PairMechanismLabel:
    return PairMechanismLabel(
        pair_id="PAIR-0001",
        source_assessment_ids=[
            "MEA-0001",
        ],
        mechanism_normalized=(
            MechanismLabel.Z_SCHEME
        ),
        charge_transfer_class=(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        ),
        has_disagreement=False,
    )


# ---------------------------------------------------------------------------
# ACCEPT PAIR LABEL
# ---------------------------------------------------------------------------
def test_accept_pair_label():
    label = accept_pair_mechanism_label(
        make_pending_label(),
        reviewer_notes=(
            "Mechanism and ML class "
            "confirmed."
        ),
    )

    assert (
        label.manual_review_status
        == ManualReviewStatus.REVIEWED
    )

    assert (
        label.label_status
        == LabelStatus.ACCEPTED
    )

    assert (
        label.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        label.charge_transfer_class
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )


# ---------------------------------------------------------------------------
# ACCEPT LABEL WITH CURATOR OVERRIDE
# ---------------------------------------------------------------------------
def test_accept_pair_label_with_override():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
        source_assessment_ids=[
            "MEA-0001",
            "MEA-0002",
        ],
        mechanism_normalized=None,
        charge_transfer_class=None,
        has_disagreement=True,
    )

    reviewed = accept_pair_mechanism_label(
        label=label,
        mechanism_normalized=(
            MechanismLabel.TYPE_II
        ),
        charge_transfer_class=(
            ChargeTransferClass.TYPE_II
        ),
        reviewer_notes=(
            "Conflicting reports reviewed; "
            "Type-II retained."
        ),
    )

    assert (
        reviewed.mechanism_normalized
        == MechanismLabel.TYPE_II
    )

    assert (
        reviewed.charge_transfer_class
        == ChargeTransferClass.TYPE_II
    )

    assert (
        reviewed.has_disagreement
        is False
    )

    assert (
        reviewed.label_status
        == LabelStatus.ACCEPTED
    )


# ---------------------------------------------------------------------------
# CANNOT ACCEPT UNRESOLVED MECHANISM
# ---------------------------------------------------------------------------
def test_cannot_accept_unresolved_mechanism():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
        mechanism_normalized=None,
        charge_transfer_class=(
            ChargeTransferClass.TYPE_II
        ),
    )

    with pytest.raises(
        ValueError,
        match="resolved mechanism",
    ):
        accept_pair_mechanism_label(
            label
        )


# ---------------------------------------------------------------------------
# CANNOT ACCEPT WITHOUT ML CLASS
# ---------------------------------------------------------------------------
def test_cannot_accept_without_ml_class():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
        mechanism_normalized=(
            MechanismLabel.Z_SCHEME
        ),
        charge_transfer_class=None,
    )

    with pytest.raises(
        ValueError,
        match="charge-transfer class",
    ):
        accept_pair_mechanism_label(
            label
        )


# ---------------------------------------------------------------------------
# MARK PAIR LABEL UNCERTAIN
# ---------------------------------------------------------------------------
def test_mark_pair_label_uncertain():
    label = (
        mark_pair_mechanism_label_uncertain(
            make_pending_label(),
            reviewer_notes=(
                "Evidence is insufficient "
                "for final acceptance."
            ),
        )
    )

    assert (
        label.manual_review_status
        == ManualReviewStatus.REVIEWED
    )

    assert (
        label.label_status
        == LabelStatus.UNCERTAIN
    )


# ---------------------------------------------------------------------------
# EXCLUDE PAIR LABEL
# ---------------------------------------------------------------------------
def test_exclude_pair_label():
    label = exclude_pair_mechanism_label(
        make_pending_label(),
        reviewer_notes=(
            "Pair is outside the "
            "curated training scope."
        ),
    )

    assert (
        label.manual_review_status
        == ManualReviewStatus.REVIEWED
    )

    assert (
        label.label_status
        == LabelStatus.EXCLUDED
    )


# ---------------------------------------------------------------------------
# EXCLUSION REQUIRES NOTES
# ---------------------------------------------------------------------------
def test_exclusion_requires_notes():
    with pytest.raises(
        ValueError,
        match="requires reviewer notes",
    ):
        exclude_pair_mechanism_label(
            make_pending_label(),
            reviewer_notes="",
        )

