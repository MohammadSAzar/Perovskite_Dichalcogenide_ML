from psk_tmd.common.constants import (
    ChargeTransferClass,
    MechanismLabel,
)
from psk_tmd.common.models import (
    ExperimentalSample,
    MechanismAssessment,
)
from psk_tmd.corpus.mechanism_aggregation import (
    aggregate_mechanisms_by_pair,
    aggregate_pair_mechanisms,
    group_assessments_by_pair,
)


# ---------------------------------------------------------------------------
# MAKE ASSESSMENT
# ---------------------------------------------------------------------------
def make_assessment(
    assessment_id: str,
    mechanism: MechanismLabel,
    charge_class: (
        ChargeTransferClass | None
    ) = None,
) -> MechanismAssessment:
    return MechanismAssessment(
        mechanism_assessment_id=(
            assessment_id
        ),
        sample_id="SMP-0001",
        applies_to_series_id=None,
        mechanism_reported=(
            mechanism.value
        ),
        mechanism_normalized=(
            mechanism
        ),
        charge_transfer_class=(
            charge_class
        ),
        claim_explicit=True,
        assessment_confidence=None,
        reviewer_notes=None,
    )


# ---------------------------------------------------------------------------
# MAKE SAMPLE
# ---------------------------------------------------------------------------
def make_sample(
    sample_id: str,
    pair_id: str | None,
) -> ExperimentalSample:
    return (
        ExperimentalSample
        .model_construct(
            sample_id=sample_id,
            paper_id="PPR-0001",
            sample_series_id=None,
            sample_name_reported=None,
            pair_id=pair_id,
            psk_fraction=None,
            tmd_fraction=None,
            fraction_basis=None,
            notes=None,
        )
    )


# ---------------------------------------------------------------------------
# SINGLE MECHANISM CONSENSUS
# ---------------------------------------------------------------------------
def test_single_mechanism_consensus():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                assessment_id=(
                    "MEA-0001"
                ),
                mechanism=(
                    MechanismLabel.Z_SCHEME
                ),
            ),
        ],
    )

    assert (
        result.mechanism_consensus
        == MechanismLabel.Z_SCHEME
    )

    assert (
        result.has_disagreement
        is False
    )


# ---------------------------------------------------------------------------
# REPEATED LABELS COLLAPSE
# ---------------------------------------------------------------------------
def test_repeated_labels_collapse():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                "MEA-0001",
                MechanismLabel.Z_SCHEME,
            ),
            make_assessment(
                "MEA-0002",
                MechanismLabel.Z_SCHEME,
            ),
        ],
    )

    assert (
        result.mechanism_labels
        == [
            MechanismLabel.Z_SCHEME
        ]
    )

    assert (
        result.mechanism_consensus
        == MechanismLabel.Z_SCHEME
    )


# ---------------------------------------------------------------------------
# CONTRADICTORY MECHANISMS
# ---------------------------------------------------------------------------
def test_contradictory_mechanisms():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                "MEA-0001",
                MechanismLabel.Z_SCHEME,
            ),
            make_assessment(
                "MEA-0002",
                MechanismLabel.TYPE_II,
            ),
        ],
    )

    assert (
        result.mechanism_consensus
        is None
    )

    assert (
        result.has_disagreement
        is True
    )


# ---------------------------------------------------------------------------
# UNKNOWN DOES NOT CREATE DISAGREEMENT
# ---------------------------------------------------------------------------
def test_unknown_does_not_create_disagreement():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                "MEA-0001",
                MechanismLabel.Z_SCHEME,
            ),
            make_assessment(
                "MEA-0002",
                MechanismLabel.UNKNOWN,
            ),
        ],
    )

    assert (
        result.mechanism_consensus
        == MechanismLabel.Z_SCHEME
    )

    assert (
        result.has_disagreement
        is False
    )


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER CONSENSUS
# ---------------------------------------------------------------------------
def test_charge_transfer_consensus():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                "MEA-0001",
                MechanismLabel.Z_SCHEME,
                ChargeTransferClass.MEDIATED_RECOMBINATION,
            ),
            make_assessment(
                "MEA-0002",
                MechanismLabel.S_SCHEME,
                ChargeTransferClass.MEDIATED_RECOMBINATION,
            ),
        ],
    )

    assert (
        result.charge_transfer_consensus
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )

    assert (
        result.mechanism_consensus
        is None
    )

    assert (
        result.has_disagreement
        is True
    )


# ---------------------------------------------------------------------------
# CONTRADICTORY CHARGE-TRANSFER CLASSES
# ---------------------------------------------------------------------------
def test_contradictory_charge_transfer_classes():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[
            make_assessment(
                "MEA-0001",
                MechanismLabel.Z_SCHEME,
                ChargeTransferClass.MEDIATED_RECOMBINATION,
            ),
            make_assessment(
                "MEA-0002",
                MechanismLabel.TYPE_II,
                ChargeTransferClass.TYPE_II,
            ),
        ],
    )

    assert (
        result.charge_transfer_consensus
        is None
    )

    assert (
        result.has_disagreement
        is True
    )


# ---------------------------------------------------------------------------
# NO ASSESSMENTS
# ---------------------------------------------------------------------------
def test_no_assessments():
    result = aggregate_pair_mechanisms(
        pair_id="PAIR-0001",
        assessments=[],
    )

    assert (
        result.assessment_ids
        == []
    )

    assert (
        result.mechanism_labels
        == []
    )

    assert (
        result.charge_transfer_classes
        == []
    )

    assert (
        result.mechanism_consensus
        is None
    )

    assert (
        result.charge_transfer_consensus
        is None
    )

    assert (
        result.has_disagreement
        is False
    )


# ---------------------------------------------------------------------------
# GROUP ASSESSMENTS BY PAIR
# ---------------------------------------------------------------------------
def test_group_assessments_by_pair():
    samples = [
        make_sample(
            "SMP-0001",
            "PAIR-0001",
        ),
        make_sample(
            "SMP-0002",
            "PAIR-0001",
        ),
        make_sample(
            "SMP-0003",
            "PAIR-0002",
        ),
    ]

    assessments = [
        make_assessment(
            "MEA-0001",
            MechanismLabel.Z_SCHEME,
        ),
        MechanismAssessment(
            mechanism_assessment_id=(
                "MEA-0002"
            ),
            sample_id="SMP-0002",
            mechanism_reported=(
                "Z-scheme"
            ),
            mechanism_normalized=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_class=None,
        ),
        MechanismAssessment(
            mechanism_assessment_id=(
                "MEA-0003"
            ),
            sample_id="SMP-0003",
            mechanism_reported=(
                "type-II"
            ),
            mechanism_normalized=(
                MechanismLabel.TYPE_II
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_II
            ),
        ),
    ]

    grouped, unresolved = (
        group_assessments_by_pair(
            samples=samples,
            assessments=assessments,
        )
    )

    assert (
        len(
            grouped[
                "PAIR-0001"
            ]
        )
        == 2
    )

    assert (
        len(
            grouped[
                "PAIR-0002"
            ]
        )
        == 1
    )

    assert unresolved == []


# ---------------------------------------------------------------------------
# MISSING SAMPLE IS UNRESOLVED
# ---------------------------------------------------------------------------
def test_missing_sample_is_unresolved():
    assessment = (
        MechanismAssessment(
            mechanism_assessment_id=(
                "MEA-9999"
            ),
            sample_id="SMP-9999",
            mechanism_reported=(
                "Z-scheme"
            ),
            mechanism_normalized=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_class=None,
        )
    )

    grouped, unresolved = (
        group_assessments_by_pair(
            samples=[],
            assessments=[
                assessment
            ],
        )
    )

    assert grouped == {}

    assert (
        unresolved
        == [
            "MEA-9999"
        ]
    )


# ---------------------------------------------------------------------------
# SAMPLE WITHOUT PAIR IS UNRESOLVED
# ---------------------------------------------------------------------------
def test_sample_without_pair_is_unresolved():
    sample = make_sample(
        "SMP-0001",
        None,
    )

    assessment = (
        make_assessment(
            "MEA-0001",
            MechanismLabel.Z_SCHEME,
        )
    )

    grouped, unresolved = (
        group_assessments_by_pair(
            samples=[
                sample
            ],
            assessments=[
                assessment
            ],
        )
    )

    assert grouped == {}

    assert (
        unresolved
        == [
            "MEA-0001"
        ]
    )


# ---------------------------------------------------------------------------
# AGGREGATE MULTIPLE PAIRS
# ---------------------------------------------------------------------------
def test_aggregate_multiple_pairs():
    samples = [
        make_sample(
            "SMP-0001",
            "PAIR-0001",
        ),
        make_sample(
            "SMP-0002",
            "PAIR-0001",
        ),
        make_sample(
            "SMP-0003",
            "PAIR-0002",
        ),
    ]

    assessments = [
        make_assessment(
            "MEA-0001",
            MechanismLabel.Z_SCHEME,
            (
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        ),
        MechanismAssessment(
            mechanism_assessment_id=(
                "MEA-0002"
            ),
            sample_id="SMP-0002",
            mechanism_reported=(
                "Z-scheme"
            ),
            mechanism_normalized=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_class=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
        ),
        MechanismAssessment(
            mechanism_assessment_id=(
                "MEA-0003"
            ),
            sample_id="SMP-0003",
            mechanism_reported=(
                "type-II"
            ),
            mechanism_normalized=(
                MechanismLabel.TYPE_II
            ),
            charge_transfer_class=(
                ChargeTransferClass.TYPE_II
            ),
        ),
    ]

    result = (
        aggregate_mechanisms_by_pair(
            samples=samples,
            assessments=assessments,
        )
    )

    assert (
        len(
            result.pair_results
        )
        == 2
    )

    pair_1 = (
        result.pair_results[
            0
        ]
    )

    pair_2 = (
        result.pair_results[
            1
        ]
    )

    assert (
        pair_1.pair_id
        == "PAIR-0001"
    )

    assert (
        pair_1.mechanism_consensus
        == MechanismLabel.Z_SCHEME
    )

    assert (
        pair_1.charge_transfer_consensus
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )

    assert (
        pair_2.pair_id
        == "PAIR-0002"
    )

    assert (
        pair_2.mechanism_consensus
        == MechanismLabel.TYPE_II
    )

    assert (
        pair_2.charge_transfer_consensus
        == ChargeTransferClass.TYPE_II
    )

    assert (
        result.unresolved_assessment_ids
        == []
    )

