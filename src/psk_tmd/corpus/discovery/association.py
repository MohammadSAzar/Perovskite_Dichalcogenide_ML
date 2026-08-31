from dataclasses import (
    dataclass,
)

from psk_tmd.corpus.discovery.material_signals import (
    detect_material_signals,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
    DiscoveryScreeningStatus,
)


# ---------------------------------------------------------------------------
# ASSOCIATION RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryAssociationResult:
    has_title_perovskite_signal: bool

    has_title_known_perovskite_formula: bool

    has_title_tmd_signal: bool

    has_title_pair_signal: bool

    matched_title_perovskite_terms: tuple[
        str,
        ...
    ]

    matched_title_abo3_formulas: tuple[
        str,
        ...
    ]

    matched_title_known_perovskite_formulas: tuple[
        str,
        ...
    ]

    matched_title_tmd_terms: tuple[
        str,
        ...
    ]


# ---------------------------------------------------------------------------
# DETECT TITLE ASSOCIATION
# ---------------------------------------------------------------------------
def detect_title_association(
    record: DiscoveryRecord,
) -> DiscoveryAssociationResult:
    title_signals = (
        detect_material_signals(
            record.title
        )
    )

    has_title_known_perovskite_formula = bool(
        title_signals
        .matched_known_perovskite_formulas
    )

    has_title_pair_signal = bool(
        (
            title_signals.has_perovskite_signal
            or has_title_known_perovskite_formula
        )
        and title_signals.has_tmd_signal
    )

    return DiscoveryAssociationResult(
        has_title_perovskite_signal=(
            title_signals
            .has_perovskite_signal
        ),
        has_title_known_perovskite_formula=(
            has_title_known_perovskite_formula
        ),
        has_title_tmd_signal=(
            title_signals
            .has_tmd_signal
        ),
        has_title_pair_signal=(
            has_title_pair_signal
        ),
        matched_title_perovskite_terms=(
            title_signals
            .matched_perovskite_terms
        ),
        matched_title_abo3_formulas=(
            title_signals
            .matched_abo3_formulas
        ),
        matched_title_known_perovskite_formulas=(
            title_signals
            .matched_known_perovskite_formulas
        ),
        matched_title_tmd_terms=(
            title_signals
            .matched_tmd_terms
        ),
    )


# ---------------------------------------------------------------------------
# RESOLVE ASSOCIATION STATUS
# ---------------------------------------------------------------------------
def resolve_association_status(
    screening: DiscoveryScreeningResult,
    association: DiscoveryAssociationResult,
) -> tuple[
    DiscoveryScreeningStatus,
    str,
]:
    if (
        screening.status
        == DiscoveryScreeningStatus.REJECT
    ):
        return (
            DiscoveryScreeningStatus.REJECT,
            screening.reason,
        )

    if (
        screening.status
        == DiscoveryScreeningStatus.REVIEW
    ):
        return (
            DiscoveryScreeningStatus.REVIEW,
            screening.reason,
        )

    if association.has_title_pair_signal:
        return (
            DiscoveryScreeningStatus.PASS,
            (
                "High-confidence screening evidence and "
                "PSK-TMD association were detected in the title."
            ),
        )

    return (
        DiscoveryScreeningStatus.REVIEW,
        (
            "High-confidence PSK, TMD, and photo signals were "
            "detected in metadata, but PSK-TMD association was "
            "not established from the title."
        ),
    )

