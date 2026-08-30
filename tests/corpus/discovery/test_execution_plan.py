import pytest

from psk_tmd.corpus.discovery.execution_plan import (
    QueryExecutionItem,
    build_execution_plan,
    is_pilot_query,
    select_pilot_queries,
)
from psk_tmd.corpus.discovery.query_strategy import (
    DiscoveryQuery,
    build_default_discovery_queries,
)


# ---------------------------------------------------------------------------
# MAKE QUERY
# ---------------------------------------------------------------------------
def make_query(
    *,
    family: str,
    perovskite_term: str,
    tmd_term: str,
    photo_term: str,
) -> DiscoveryQuery:
    return DiscoveryQuery(
        query_id="QRY-000001",
        family=family,
        perovskite_term=perovskite_term,
        tmd_term=tmd_term,
        photo_term=photo_term,
        query_text=(
            f"{perovskite_term} "
            f"{tmd_term} "
            f"{photo_term}"
        ),
    )


# ---------------------------------------------------------------------------
# GENERIC PILOT QUERY INCLUDED
# ---------------------------------------------------------------------------
def test_generic_pilot_query_included():
    query = make_query(
        family="generic_perovskite",
        perovskite_term="perovskite",
        tmd_term="MoS2",
        photo_term="photocatalysis",
    )

    assert (
        is_pilot_query(
            query
        )
        is True
    )


# ---------------------------------------------------------------------------
# SEED PILOT QUERY INCLUDED
# ---------------------------------------------------------------------------
def test_seed_pilot_query_included():
    query = make_query(
        family="seed_perovskite",
        perovskite_term="CaTiO3",
        tmd_term="WS2",
        photo_term="hydrogen evolution",
    )

    assert (
        is_pilot_query(
            query
        )
        is True
    )


# ---------------------------------------------------------------------------
# NON-PILOT TMD EXCLUDED
# ---------------------------------------------------------------------------
def test_non_pilot_tmd_excluded():
    query = make_query(
        family="seed_perovskite",
        perovskite_term="CaTiO3",
        tmd_term="MoSe2",
        photo_term="photocatalysis",
    )

    assert (
        is_pilot_query(
            query
        )
        is False
    )


# ---------------------------------------------------------------------------
# NON-PILOT PHOTO TERM EXCLUDED
# ---------------------------------------------------------------------------
def test_non_pilot_photo_term_excluded():
    query = make_query(
        family="seed_perovskite",
        perovskite_term="CaTiO3",
        tmd_term="MoS2",
        photo_term="CO2 reduction",
    )

    assert (
        is_pilot_query(
            query
        )
        is False
    )


# ---------------------------------------------------------------------------
# SELECT PILOT QUERY COUNT
# ---------------------------------------------------------------------------
def test_select_pilot_query_count():
    queries = (
        build_default_discovery_queries()
    )

    pilot_queries = (
        select_pilot_queries(
            queries
        )
    )

    assert len(
        pilot_queries
    ) == 48


# ---------------------------------------------------------------------------
# PILOT QUERY IDS REMAIN ORIGINAL
# ---------------------------------------------------------------------------
def test_pilot_query_ids_remain_original():
    queries = (
        build_default_discovery_queries()
    )

    pilot_queries = (
        select_pilot_queries(
            queries
        )
    )

    original_ids = {
        query.query_id
        for query in queries
    }

    assert all(
        query.query_id
        in original_ids
        for query in pilot_queries
    )


# ---------------------------------------------------------------------------
# BUILD EXECUTION PLAN
# ---------------------------------------------------------------------------
def test_build_execution_plan():
    queries = (
        select_pilot_queries(
            build_default_discovery_queries()
        )
    )

    plan = (
        build_execution_plan(
            queries
        )
    )

    assert len(
        plan
    ) == 48

    assert isinstance(
        plan[
            0
        ],
        QueryExecutionItem,
    )

    assert (
        plan[
            0
        ].execution_index
        == 1
    )

    assert (
        plan[
            -1
        ].execution_index
        == 48
    )

    assert (
        plan[
            0
        ].sources
        == (
            "crossref",
            "openalex",
        )
    )


# ---------------------------------------------------------------------------
# CUSTOM SOURCES NORMALIZED
# ---------------------------------------------------------------------------
def test_custom_sources_normalized():
    query = make_query(
        family="generic_perovskite",
        perovskite_term="perovskite",
        tmd_term="MoS2",
        photo_term="photocatalysis",
    )

    plan = build_execution_plan(
        [
            query,
        ],
        sources=(
            " Crossref ",
            "OPENALEX",
        ),
    )

    assert (
        plan[
            0
        ].sources
        == (
            "crossref",
            "openalex",
        )
    )


# ---------------------------------------------------------------------------
# EMPTY SOURCES FAIL
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "sources",
    [
        (),
        (
            "   ",
        ),
    ],
)
def test_empty_sources_fail(
    sources,
):
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        build_execution_plan(
            [],
            sources=sources,
        )


# ---------------------------------------------------------------------------
# DUPLICATE SOURCES FAIL
# ---------------------------------------------------------------------------
def test_duplicate_sources_fail():
    with pytest.raises(
        ValueError,
        match="must be unique",
    ):
        build_execution_plan(
            [],
            sources=(
                "crossref",
                "Crossref",
            ),
        )

