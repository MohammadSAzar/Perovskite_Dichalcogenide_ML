from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    ChargeTransferClass,
    MechanismLabel,
)
from psk_tmd.common.models import (
    ExperimentalSample,
    MechanismAssessment,
)


# ---------------------------------------------------------------------------
# PAIR MECHANISM AGGREGATION RESULT
# ---------------------------------------------------------------------------
class PairMechanismAggregationResult(
    BaseModel
):
    pair_id: str

    assessment_ids: list[
        str
    ] = Field(
        default_factory=list,
    )

    mechanism_labels: list[
        MechanismLabel
    ] = Field(
        default_factory=list,
    )

    charge_transfer_classes: list[
        ChargeTransferClass
    ] = Field(
        default_factory=list,
    )

    mechanism_consensus: (
        MechanismLabel | None
    ) = None

    charge_transfer_consensus: (
        ChargeTransferClass | None
    ) = None

    has_disagreement: bool = False


# ---------------------------------------------------------------------------
# PAIR MECHANISM LINKAGE RESULT
# ---------------------------------------------------------------------------
class PairMechanismLinkageResult(
    BaseModel
):
    pair_results: list[
        PairMechanismAggregationResult
    ] = Field(
        default_factory=list,
    )

    unresolved_assessment_ids: list[
        str
    ] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# UNIQUE MECHANISM LABELS
# ---------------------------------------------------------------------------
def collect_mechanism_labels(
    assessments: list[
        MechanismAssessment
    ],
) -> list[
    MechanismLabel
]:
    labels: list[
        MechanismLabel
    ] = []

    for assessment in assessments:
        label = (
            assessment
            .mechanism_normalized
        )

        if (
            label
            == MechanismLabel.UNKNOWN
        ):
            continue

        if label not in labels:
            labels.append(
                label
            )

    return labels


# ---------------------------------------------------------------------------
# UNIQUE CHARGE-TRANSFER CLASSES
# ---------------------------------------------------------------------------
def collect_charge_transfer_classes(
    assessments: list[
        MechanismAssessment
    ],
) -> list[
    ChargeTransferClass
]:
    classes: list[
        ChargeTransferClass
    ] = []

    for assessment in assessments:
        charge_class = (
            assessment
            .charge_transfer_class
        )

        if charge_class is None:
            continue

        if charge_class not in classes:
            classes.append(
                charge_class
            )

    return classes


# ---------------------------------------------------------------------------
# AGGREGATE PAIR MECHANISMS
# ---------------------------------------------------------------------------
def aggregate_pair_mechanisms(
    pair_id: str,
    assessments: list[
        MechanismAssessment
    ],
) -> PairMechanismAggregationResult:
    mechanism_labels = (
        collect_mechanism_labels(
            assessments
        )
    )

    charge_transfer_classes = (
        collect_charge_transfer_classes(
            assessments
        )
    )

    if len(
        mechanism_labels
    ) == 1:
        mechanism_consensus = (
            mechanism_labels[
                0
            ]
        )

    else:
        mechanism_consensus = None

    if len(
        charge_transfer_classes
    ) == 1:
        charge_transfer_consensus = (
            charge_transfer_classes[
                0
            ]
        )

    else:
        charge_transfer_consensus = None

    has_disagreement = (
        len(
            mechanism_labels
        )
        > 1
        or len(
            charge_transfer_classes
        )
        > 1
    )

    return PairMechanismAggregationResult(
        pair_id=pair_id,
        assessment_ids=[
            assessment
            .mechanism_assessment_id
            for assessment
            in assessments
        ],
        mechanism_labels=(
            mechanism_labels
        ),
        charge_transfer_classes=(
            charge_transfer_classes
        ),
        mechanism_consensus=(
            mechanism_consensus
        ),
        charge_transfer_consensus=(
            charge_transfer_consensus
        ),
        has_disagreement=(
            has_disagreement
        ),
    )


# ---------------------------------------------------------------------------
# GROUP ASSESSMENTS BY PAIR
# ---------------------------------------------------------------------------
def group_assessments_by_pair(
    samples: list[
        ExperimentalSample
    ],
    assessments: list[
        MechanismAssessment
    ],
) -> tuple[
    dict[
        str,
        list[
            MechanismAssessment
        ],
    ],
    list[str],
]:
    sample_pair_lookup = {
        sample.sample_id: (
            sample.pair_id
        )
        for sample in samples
    }

    grouped: dict[
        str,
        list[
            MechanismAssessment
        ],
    ] = {}

    unresolved_assessment_ids: list[
        str
    ] = []

    for assessment in assessments:
        pair_id = (
            sample_pair_lookup.get(
                assessment.sample_id
            )
        )

        if pair_id is None:
            unresolved_assessment_ids.append(
                assessment
                .mechanism_assessment_id
            )

            continue

        if pair_id not in grouped:
            grouped[pair_id] = []

        grouped[pair_id].append(
            assessment
        )

    return (
        grouped,
        unresolved_assessment_ids,
    )


# ---------------------------------------------------------------------------
# AGGREGATE MECHANISMS BY PAIR
# ---------------------------------------------------------------------------
def aggregate_mechanisms_by_pair(
    samples: list[
        ExperimentalSample
    ],
    assessments: list[
        MechanismAssessment
    ],
) -> PairMechanismLinkageResult:
    (
        grouped,
        unresolved_assessment_ids,
    ) = group_assessments_by_pair(
        samples=samples,
        assessments=assessments,
    )

    pair_results = [
        aggregate_pair_mechanisms(
            pair_id=pair_id,
            assessments=(
                pair_assessments
            ),
        )
        for pair_id, pair_assessments
        in sorted(
            grouped.items()
        )
    ]

    return PairMechanismLinkageResult(
        pair_results=pair_results,
        unresolved_assessment_ids=(
            unresolved_assessment_ids
        ),
    )


