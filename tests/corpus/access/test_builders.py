import pytest

from psk_tmd.corpus.access.builders import (
    build_access_id,
    build_access_records_from_selection,
    build_initial_access_record,
    build_initial_access_records,
)
from psk_tmd.corpus.access.models import (
    AccessStatus,
    AcquisitionRoute,
    TDMStatus,
)
from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningResult,
    DiscoveryScreeningStatus,
)
from psk_tmd.corpus.discovery.selection import (
    DiscoveryCandidateSelection,
)


# ---------------------------------------------------------------------------
# MAKE CANDIDATE
# ---------------------------------------------------------------------------
def make_candidate(
    candidate_id: str,
    *,
    doi: str | None = None,
    publisher: str | None = None,
    is_open_access: bool | None = None,
) -> DiscoveryCandidate:
    record = DiscoveryRecord(
        discovery_id=(
            candidate_id
        ),
        doi=doi,
        title="Test discovery paper",
        publisher=publisher,
        source="test",
        is_open_access=(
            is_open_access
        ),
    )

    return DiscoveryCandidate(
        candidate_id=(
            candidate_id
        ),
        group_key=(
            f"candidate:"
            f"{candidate_id}"
        ),
        record=record,
        hit_count=1,
        query_ids=(
            "QRY-000001",
        ),
        query_texts=(
            "test query",
        ),
        families=(
            "test_family",
        ),
        sources=(
            "test",
        ),
        source_ranks=(),
    )


# ---------------------------------------------------------------------------
# MAKE SCREENING
# ---------------------------------------------------------------------------
def make_screening(
    candidate_id: str,
    status: DiscoveryScreeningStatus,
) -> DiscoveryScreeningResult:
    return DiscoveryScreeningResult(
        discovery_id=(
            candidate_id
        ),
        status=status,
        has_perovskite_signal=True,
        has_oxide_perovskite_signal=(
            status
            == DiscoveryScreeningStatus.PASS
        ),
        has_halide_perovskite_signal=False,
        has_tmd_signal=True,
        has_photo_signal=True,
        matched_perovskite_terms=(),
        matched_abo3_formulas=(),
        matched_known_perovskite_formulas=(),
        matched_oxide_perovskite_terms=(),
        matched_halide_perovskite_terms=(),
        matched_halide_perovskite_formulas=(),
        matched_tmd_terms=(
            "mos2",
        ),
        matched_photo_terms=(
            "photocatalytic",
        ),
        reason="Test screening result.",
    )


# ---------------------------------------------------------------------------
# BUILD ACCESS ID
# ---------------------------------------------------------------------------
def test_build_access_id():
    assert (
        build_access_id(
            1
        )
        == "ACC-000001"
    )

    assert (
        build_access_id(
            42
        )
        == "ACC-000042"
    )


# ---------------------------------------------------------------------------
# INVALID ACCESS ID INDEX
# ---------------------------------------------------------------------------
def test_invalid_access_id_index():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_access_id(
            0
        )


# ---------------------------------------------------------------------------
# BUILD INITIAL ACCESS RECORD
# ---------------------------------------------------------------------------
def test_build_initial_access_record():
    candidate = (
        make_candidate(
            "CND-000001",
            doi=(
                "10.1000/example"
            ),
            publisher=(
                "Example Publisher"
            ),
            is_open_access=True,
        )
    )

    screening = (
        make_screening(
            "CND-000001",
            DiscoveryScreeningStatus.PASS,
        )
    )

    access_record = (
        build_initial_access_record(
            candidate,
            screening,
            access_id=(
                "ACC-000001"
            ),
        )
    )

    assert (
        access_record.access_id
        == "ACC-000001"
    )

    assert (
        access_record.candidate_id
        == "CND-000001"
    )

    assert (
        access_record.doi
        == "10.1000/example"
    )

    assert (
        access_record.publisher
        == "Example Publisher"
    )

    assert (
        access_record.is_open_access
        is True
    )

    assert (
        access_record.access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        access_record.acquisition_route
        == AcquisitionRoute.NONE
    )

    assert (
        access_record.tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        access_record.full_text_available
        is False
    )


# ---------------------------------------------------------------------------
# OA DISCOVERY SIGNAL DOES NOT RESOLVE ACCESS
# ---------------------------------------------------------------------------
def test_oa_discovery_signal_does_not_resolve_access():
    candidate = (
        make_candidate(
            "CND-000001",
            is_open_access=True,
        )
    )

    screening = (
        make_screening(
            "CND-000001",
            DiscoveryScreeningStatus.PASS,
        )
    )

    access_record = (
        build_initial_access_record(
            candidate,
            screening,
            access_id=(
                "ACC-000001"
            ),
        )
    )

    assert (
        access_record.is_open_access
        is True
    )

    assert (
        access_record.access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        access_record.tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        access_record.full_text_available
        is False
    )


# ---------------------------------------------------------------------------
# BUILD INITIAL ACCESS RECORDS
# ---------------------------------------------------------------------------
def test_build_initial_access_records():
    first_candidate = (
        make_candidate(
            "CND-000001"
        )
    )

    second_candidate = (
        make_candidate(
            "CND-000002"
        )
    )

    actionable = [
        (
            first_candidate,
            make_screening(
                "CND-000001",
                DiscoveryScreeningStatus.PASS,
            ),
        ),
        (
            second_candidate,
            make_screening(
                "CND-000002",
                DiscoveryScreeningStatus.REVIEW,
            ),
        ),
    ]

    access_records = (
        build_initial_access_records(
            actionable
        )
    )

    assert len(
        access_records
    ) == 2

    assert (
        access_records[
            0
        ].access_id
        == "ACC-000001"
    )

    assert (
        access_records[
            1
        ].access_id
        == "ACC-000002"
    )

    assert (
        access_records[
            0
        ].candidate_id
        == "CND-000001"
    )

    assert (
        access_records[
            1
        ].candidate_id
        == "CND-000002"
    )


# ---------------------------------------------------------------------------
# CUSTOM START INDEX
# ---------------------------------------------------------------------------
def test_custom_start_index():
    candidate = (
        make_candidate(
            "CND-000010"
        )
    )

    actionable = [
        (
            candidate,
            make_screening(
                "CND-000010",
                DiscoveryScreeningStatus.PASS,
            ),
        )
    ]

    access_records = (
        build_initial_access_records(
            actionable,
            start_index=10,
        )
    )

    assert (
        access_records[
            0
        ].access_id
        == "ACC-000010"
    )


# ---------------------------------------------------------------------------
# INVALID START INDEX
# ---------------------------------------------------------------------------
def test_invalid_start_index():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_initial_access_records(
            [],
            start_index=0,
        )


# ---------------------------------------------------------------------------
# BUILD FROM SELECTION
# ---------------------------------------------------------------------------
def test_build_access_records_from_selection():
    accepted_candidate = (
        make_candidate(
            "CND-000001"
        )
    )

    review_candidate = (
        make_candidate(
            "CND-000002"
        )
    )

    rejected_candidate = (
        make_candidate(
            "CND-000003"
        )
    )

    selection = (
        DiscoveryCandidateSelection(
            accepted=(
                (
                    accepted_candidate,
                    make_screening(
                        "CND-000001",
                        DiscoveryScreeningStatus.PASS,
                    ),
                ),
            ),
            review=(
                (
                    review_candidate,
                    make_screening(
                        "CND-000002",
                        DiscoveryScreeningStatus.REVIEW,
                    ),
                ),
            ),
            rejected=(
                (
                    rejected_candidate,
                    make_screening(
                        "CND-000003",
                        DiscoveryScreeningStatus.REJECT,
                    ),
                ),
            ),
        )
    )

    access_records = (
        build_access_records_from_selection(
            selection
        )
    )

    candidate_ids = [
        record.candidate_id
        for record in access_records
    ]

    assert candidate_ids == [
        "CND-000001",
        "CND-000002",
    ]


# ---------------------------------------------------------------------------
# REJECTED CANDIDATES ARE NOT INCLUDED
# ---------------------------------------------------------------------------
def test_rejected_candidates_are_not_included():
    rejected_candidate = (
        make_candidate(
            "CND-000003"
        )
    )

    selection = (
        DiscoveryCandidateSelection(
            accepted=(),
            review=(),
            rejected=(
                (
                    rejected_candidate,
                    make_screening(
                        "CND-000003",
                        DiscoveryScreeningStatus.REJECT,
                    ),
                ),
            ),
        )
    )

    access_records = (
        build_access_records_from_selection(
            selection
        )
    )

    assert (
        access_records
        == []
    )

