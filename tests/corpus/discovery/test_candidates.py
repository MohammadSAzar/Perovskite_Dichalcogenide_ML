import pytest

from psk_tmd.corpus.discovery.candidates import (
    DiscoveryCandidate,
    build_discovery_candidate,
    build_discovery_candidates,
    build_source_ranks,
    group_discovery_hits,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.runner import (
    DiscoveryHit,
)


# ---------------------------------------------------------------------------
# MAKE DISCOVERY HIT
# ---------------------------------------------------------------------------
def make_hit(
    *,
    query_id: str,
    query_text: str,
    source: str,
    source_rank: int,
    doi: str,
    title: str = "Test paper",
    year: int | None = None,
    is_open_access: bool | None = None,
) -> DiscoveryHit:
    record = DiscoveryRecord(
        discovery_id=(
            f"{source}-record"
        ),
        doi=doi,
        title=title,
        year=year,
        source=source,
        is_open_access=(
            is_open_access
        ),
    )

    return DiscoveryHit(
        query_id=query_id,
        query_text=query_text,
        family="test_family",
        source=source,
        source_rank=source_rank,
        record=record,
    )


# ---------------------------------------------------------------------------
# GROUP SAME DOI
# ---------------------------------------------------------------------------
def test_group_same_doi():
    hits = [
        make_hit(
            query_id="QRY-000001",
            query_text="query one",
            source="crossref",
            source_rank=1,
            doi="10.1000/shared",
        ),
        make_hit(
            query_id="QRY-000002",
            query_text="query two",
            source="openalex",
            source_rank=2,
            doi="10.1000/shared",
        ),
    ]

    grouped = (
        group_discovery_hits(
            hits
        )
    )

    assert len(
        grouped
    ) == 1

    assert (
        "doi:10.1000/shared"
        in grouped
    )


# ---------------------------------------------------------------------------
# BUILD SOURCE RANKS
# ---------------------------------------------------------------------------
def test_build_source_ranks_uses_best_rank():
    hits = [
        make_hit(
            query_id="QRY-000001",
            query_text="query one",
            source="crossref",
            source_rank=4,
            doi="10.1000/shared",
        ),
        make_hit(
            query_id="QRY-000002",
            query_text="query two",
            source="crossref",
            source_rank=1,
            doi="10.1000/shared",
        ),
        make_hit(
            query_id="QRY-000003",
            query_text="query three",
            source="openalex",
            source_rank=2,
            doi="10.1000/shared",
        ),
    ]

    ranks = (
        build_source_ranks(
            hits
        )
    )

    assert len(
        ranks
    ) == 2

    assert (
        ranks[
            0
        ].source
        == "crossref"
    )

    assert (
        ranks[
            0
        ].best_rank
        == 1
    )

    assert (
        ranks[
            1
        ].source
        == "openalex"
    )

    assert (
        ranks[
            1
        ].best_rank
        == 2
    )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY CANDIDATE
# ---------------------------------------------------------------------------
def test_build_discovery_candidate():
    hits = [
        make_hit(
            query_id="QRY-000001",
            query_text=(
                "perovskite MoS2 "
                "photocatalysis"
            ),
            source="crossref",
            source_rank=1,
            doi="10.1000/shared",
            year=2024,
            is_open_access=None,
        ),
        make_hit(
            query_id="QRY-000002",
            query_text=(
                "perovskite MoS2 "
                "photocatalytic"
            ),
            source="openalex",
            source_rank=2,
            doi="10.1000/shared",
            year=2023,
            is_open_access=False,
        ),
    ]

    candidate = (
        build_discovery_candidate(
            hits,
            candidate_id="CND-000001",
        )
    )

    assert isinstance(
        candidate,
        DiscoveryCandidate,
    )

    assert (
        candidate.candidate_id
        == "CND-000001"
    )

    assert (
        candidate.group_key
        == "doi:10.1000/shared"
    )

    assert (
        candidate.hit_count
        == 2
    )

    assert (
        candidate.query_ids
        == (
            "QRY-000001",
            "QRY-000002",
        )
    )

    assert (
        candidate.sources
        == (
            "crossref",
            "openalex",
        )
    )

    assert (
        candidate.record.doi
        == "10.1000/shared"
    )

    assert (
        candidate.record.year
        == 2023
    )

    assert (
        candidate.record.is_open_access
        is False
    )


# ---------------------------------------------------------------------------
# EMPTY CANDIDATE FAILS
# ---------------------------------------------------------------------------
def test_empty_candidate_fails():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        build_discovery_candidate(
            [],
            candidate_id=(
                "CND-000001"
            ),
        )


# ---------------------------------------------------------------------------
# MIXED GROUP FAILS
# ---------------------------------------------------------------------------
def test_mixed_group_fails():
    hits = [
        make_hit(
            query_id="QRY-000001",
            query_text="query one",
            source="crossref",
            source_rank=1,
            doi="10.1000/one",
        ),
        make_hit(
            query_id="QRY-000002",
            query_text="query two",
            source="openalex",
            source_rank=1,
            doi="10.1000/two",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="one group",
    ):
        build_discovery_candidate(
            hits,
            candidate_id=(
                "CND-000001"
            ),
        )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY CANDIDATES
# ---------------------------------------------------------------------------
def test_build_discovery_candidates():
    hits = [
        make_hit(
            query_id="QRY-000001",
            query_text="query one",
            source="crossref",
            source_rank=1,
            doi="10.1000/shared",
        ),
        make_hit(
            query_id="QRY-000002",
            query_text="query two",
            source="openalex",
            source_rank=1,
            doi="10.1000/shared",
        ),
        make_hit(
            query_id="QRY-000003",
            query_text="query three",
            source="crossref",
            source_rank=1,
            doi="10.1000/unique",
        ),
    ]

    candidates = (
        build_discovery_candidates(
            hits
        )
    )

    assert len(
        candidates
    ) == 2

    assert (
        candidates[
            0
        ].candidate_id
        == "CND-000001"
    )

    assert (
        candidates[
            1
        ].candidate_id
        == "CND-000002"
    )

    total_hits = sum(
        candidate.hit_count
        for candidate in candidates
    )

    assert total_hits == 3


# ---------------------------------------------------------------------------
# INVALID START INDEX FAILS
# ---------------------------------------------------------------------------
def test_invalid_start_index_fails():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_discovery_candidates(
            [],
            start_index=0,
        )

