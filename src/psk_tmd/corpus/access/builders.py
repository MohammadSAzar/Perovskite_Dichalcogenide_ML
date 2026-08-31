from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    TDMStatus,
)
from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
)
from psk_tmd.corpus.discovery.selection import (
    DiscoveryCandidateSelection,
    ScreenedCandidate,
)


# ---------------------------------------------------------------------------
# BUILD ACCESS ID
# ---------------------------------------------------------------------------
def build_access_id(
    index: int,
) -> str:
    if index < 1:
        raise ValueError(
            "Access record index "
            "must be at least 1."
        )

    return (
        f"ACC-"
        f"{index:06d}"
    )


# ---------------------------------------------------------------------------
# BUILD INITIAL ACCESS RECORD
# ---------------------------------------------------------------------------
def build_initial_access_record(
    candidate: DiscoveryCandidate,
    screening: DiscoveryScreeningResult,
    *,
    access_id: str,
) -> AccessRecord:
    record = (
        candidate.record
    )

    notes = (
        "Initial access record created "
        f"from discovery candidate "
        f"{candidate.candidate_id} "
        f"with screening status "
        f"{screening.status.value}."
    )

    return AccessRecord(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate.candidate_id
        ),
        doi=(
            record.doi
        ),
        publisher=(
            record.publisher
        ),
        is_open_access=(
            record.is_open_access
        ),
        access_status=(
            AccessStatus.REQUIRES_REVIEW
        ),
        acquisition_route=(
            AcquisitionRoute.NONE
        ),
        tdm_status=(
            TDMStatus.NOT_EVALUATED
        ),
        full_text_available=False,
        notes=(
            notes
        ),
    )


# ---------------------------------------------------------------------------
# BUILD INITIAL ACCESS RECORDS
# ---------------------------------------------------------------------------
def build_initial_access_records(
    actionable_candidates: list[
        ScreenedCandidate
    ]
    | tuple[
        ScreenedCandidate,
        ...
    ],
    *,
    start_index: int = 1,
) -> list[
    AccessRecord
]:
    if start_index < 1:
        raise ValueError(
            "Access record start_index "
            "must be at least 1."
        )

    access_records = []

    next_index = (
        start_index
    )

    for (
        candidate,
        screening,
    ) in actionable_candidates:
        access_record = (
            build_initial_access_record(
                candidate,
                screening,
                access_id=(
                    build_access_id(
                        next_index
                    )
                ),
            )
        )

        access_records.append(
            access_record
        )

        next_index += 1

    return access_records


# ---------------------------------------------------------------------------
# BUILD ACCESS RECORDS FROM SELECTION
# ---------------------------------------------------------------------------
def build_access_records_from_selection(
    selection: DiscoveryCandidateSelection,
    *,
    start_index: int = 1,
) -> list[
    AccessRecord
]:
    return (
        build_initial_access_records(
            selection.actionable,
            start_index=(
                start_index
            ),
        )
    )

