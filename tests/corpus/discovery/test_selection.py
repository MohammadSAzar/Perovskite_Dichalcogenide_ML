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
    select_discovery_candidates,
)


# ---------------------------------------------------------------------------
# MAKE CANDIDATE
# ---------------------------------------------------------------------------
def make_candidate(
    candidate_id: str,
) -> DiscoveryCandidate:
    record = DiscoveryRecord(
        discovery_id=(
            candidate_id
        ),
        doi=(
            f"10.1000/"
            f"{candidate_id.lower()}"
        ),
        title="Test paper",
        source="test",
    )

    return DiscoveryCandidate(
        candidate_id=(
            candidate_id
        ),
        group_key=(
            f"doi:"
            f"{record.doi}"
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
        matched_perovskite_formulas=(),
        matched_oxide_perovskite_terms=(),
        matched_halide_perovskite_terms=(),
        matched_halide_perovskite_formulas=(),
        matched_tmd_terms=(),
        matched_photo_terms=(),
        reason="Test reason.",
    )


# ---------------------------------------------------------------------------
# SELECT DISCOVERY CANDIDATES
# ---------------------------------------------------------------------------
def test_select_discovery_candidates():
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

    screened_candidates = [
        (
            accepted_candidate,
            make_screening(
                "CND-000001",
                DiscoveryScreeningStatus.PASS,
            ),
        ),
        (
            review_candidate,
            make_screening(
                "CND-000002",
                DiscoveryScreeningStatus.REVIEW,
            ),
        ),
        (
            rejected_candidate,
            make_screening(
                "CND-000003",
                DiscoveryScreeningStatus.REJECT,
            ),
        ),
    ]

    selection = (
        select_discovery_candidates(
            screened_candidates
        )
    )

    assert isinstance(
        selection,
        DiscoveryCandidateSelection,
    )

    assert len(
        selection.accepted
    ) == 1

    assert len(
        selection.review
    ) == 1

    assert len(
        selection.rejected
    ) == 1

    assert len(
        selection.actionable
    ) == 2


# ---------------------------------------------------------------------------
# ACTIONABLE IS PASS PLUS REVIEW
# ---------------------------------------------------------------------------
def test_actionable_is_pass_plus_review():
    accepted = (
        make_candidate(
            "CND-000001"
        )
    )

    review = (
        make_candidate(
            "CND-000002"
        )
    )

    selection = (
        select_discovery_candidates(
            [
                (
                    accepted,
                    make_screening(
                        "CND-000001",
                        DiscoveryScreeningStatus.PASS,
                    ),
                ),
                (
                    review,
                    make_screening(
                        "CND-000002",
                        DiscoveryScreeningStatus.REVIEW,
                    ),
                ),
            ]
        )
    )

    candidate_ids = [
        candidate.candidate_id
        for (
            candidate,
            _
        ) in selection.actionable
    ]

    assert candidate_ids == [
        "CND-000001",
        "CND-000002",
    ]


# ---------------------------------------------------------------------------
# EMPTY INPUT
# ---------------------------------------------------------------------------
def test_empty_input():
    selection = (
        select_discovery_candidates(
            []
        )
    )

    assert (
        selection.accepted
        == ()
    )

    assert (
        selection.review
        == ()
    )

    assert (
        selection.rejected
        == ()
    )

    assert (
        selection.actionable
        == ()
    )

