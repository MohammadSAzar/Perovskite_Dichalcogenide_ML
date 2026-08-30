import pytest

from psk_tmd.corpus.discovery.execution_plan import (
    QueryExecutionItem,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.runner import (
    DiscoveryHit,
    build_discovery_hits,
    run_discovery_plan,
)


# ---------------------------------------------------------------------------
# MAKE EXECUTION ITEM
# ---------------------------------------------------------------------------
def make_execution_item(
) -> QueryExecutionItem:
    return QueryExecutionItem(
        execution_index=1,
        query_id="QRY-000001",
        family="generic_perovskite",
        query_text=(
            "perovskite MoS2 "
            "photocatalysis"
        ),
        sources=(
            "crossref",
            "openalex",
        ),
    )


# ---------------------------------------------------------------------------
# MAKE DISCOVERY RECORD
# ---------------------------------------------------------------------------
def make_record(
    discovery_id: str,
    *,
    source: str,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        discovery_id=discovery_id,
        doi="10.1000/test",
        title="Test paper",
        source=source,
    )


# ---------------------------------------------------------------------------
# BUILD DISCOVERY HITS
# ---------------------------------------------------------------------------
def test_build_discovery_hits():
    item = (
        make_execution_item()
    )

    records = [
        make_record(
            "DSC-000001",
            source="crossref",
        ),
        make_record(
            "DSC-000002",
            source="crossref",
        ),
    ]

    hits = (
        build_discovery_hits(
            item=item,
            source="crossref",
            records=records,
        )
    )

    assert len(
        hits
    ) == 2

    assert isinstance(
        hits[
            0
        ],
        DiscoveryHit,
    )

    assert (
        hits[
            0
        ].query_id
        == "QRY-000001"
    )

    assert (
        hits[
            0
        ].source
        == "crossref"
    )

    assert (
        hits[
            0
        ].source_rank
        == 1
    )

    assert (
        hits[
            1
        ].source_rank
        == 2
    )


# ---------------------------------------------------------------------------
# RUN DISCOVERY PLAN
# ---------------------------------------------------------------------------
def test_run_discovery_plan():
    item = (
        make_execution_item()
    )

    def fake_crossref(
        query_text,
        result_limit,
    ):
        assert (
            query_text
            == (
                "perovskite MoS2 "
                "photocatalysis"
            )
        )

        assert (
            result_limit
            == 5
        )

        return [
            make_record(
                "DSC-000001",
                source="crossref",
            ),
        ]

    def fake_openalex(
        query_text,
        result_limit,
    ):
        return [
            make_record(
                "DSC-000002",
                source="openalex",
            ),
            make_record(
                "DSC-000003",
                source="openalex",
            ),
        ]

    result = run_discovery_plan(
        [
            item,
        ],
        result_limit=5,
        delay_seconds=0.0,
        source_fetchers={
            "crossref": (
                fake_crossref
            ),
            "openalex": (
                fake_openalex
            ),
        },
    )

    assert (
        result.attempted_calls
        == 2
    )

    assert (
        result.successful_calls
        == 2
    )

    assert (
        result.failed_calls
        == 0
    )

    assert len(
        result.hits
    ) == 3


# ---------------------------------------------------------------------------
# FAILED CALL DOES NOT STOP RUN
# ---------------------------------------------------------------------------
def test_failed_call_does_not_stop_run():
    item = (
        make_execution_item()
    )

    def fake_crossref(
        query_text,
        result_limit,
    ):
        raise RuntimeError(
            "Simulated failure"
        )

    def fake_openalex(
        query_text,
        result_limit,
    ):
        return [
            make_record(
                "DSC-000001",
                source="openalex",
            ),
        ]

    result = run_discovery_plan(
        [
            item,
        ],
        result_limit=5,
        delay_seconds=0.0,
        source_fetchers={
            "crossref": (
                fake_crossref
            ),
            "openalex": (
                fake_openalex
            ),
        },
    )

    assert (
        result.attempted_calls
        == 2
    )

    assert (
        result.successful_calls
        == 1
    )

    assert (
        result.failed_calls
        == 1
    )

    assert len(
        result.hits
    ) == 1

    assert (
        result.hits[
            0
        ].source
        == "openalex"
    )


# ---------------------------------------------------------------------------
# UNKNOWN SOURCE COUNTS AS FAILURE
# ---------------------------------------------------------------------------
def test_unknown_source_counts_as_failure():
    item = QueryExecutionItem(
        execution_index=1,
        query_id="QRY-000001",
        family="test",
        query_text="test query",
        sources=(
            "unknown",
        ),
    )

    result = run_discovery_plan(
        [
            item,
        ],
        delay_seconds=0.0,
        source_fetchers={},
    )

    assert (
        result.attempted_calls
        == 1
    )

    assert (
        result.successful_calls
        == 0
    )

    assert (
        result.failed_calls
        == 1
    )

    assert (
        result.hits
        == ()
    )


# ---------------------------------------------------------------------------
# INVALID RESULT LIMIT FAILS
# ---------------------------------------------------------------------------
def test_invalid_result_limit_fails():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        run_discovery_plan(
            [],
            result_limit=0,
            delay_seconds=0.0,
        )


# ---------------------------------------------------------------------------
# NEGATIVE DELAY FAILS
# ---------------------------------------------------------------------------
def test_negative_delay_fails():
    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        run_discovery_plan(
            [],
            delay_seconds=-1.0,
        )

