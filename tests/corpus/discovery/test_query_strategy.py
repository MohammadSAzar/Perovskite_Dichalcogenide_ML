import pytest

from psk_tmd.corpus.discovery.query_strategy import (
    DiscoveryQuery,
    build_default_discovery_queries,
    build_query_family,
    build_query_text,
    normalize_query_text,
)


# ---------------------------------------------------------------------------
# NORMALIZE QUERY TEXT
# ---------------------------------------------------------------------------
def test_normalize_query_text():
    result = (
        normalize_query_text(
            "  perovskite   MoS2  "
        )
    )

    assert result == (
        "perovskite MoS2"
    )


# ---------------------------------------------------------------------------
# BUILD QUERY TEXT
# ---------------------------------------------------------------------------
def test_build_query_text():
    result = (
        build_query_text(
            "CaTiO3",
            "MoS2",
            "photocatalysis",
        )
    )

    assert result == (
        "CaTiO3 MoS2 photocatalysis"
    )


# ---------------------------------------------------------------------------
# EMPTY QUERY TERM FAILS
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    (
        "perovskite_term",
        "tmd_term",
        "photo_term",
    ),
    [
        (
            "",
            "MoS2",
            "photocatalysis",
        ),
        (
            "CaTiO3",
            "",
            "photocatalysis",
        ),
        (
            "CaTiO3",
            "MoS2",
            "",
        ),
    ],
)
def test_empty_query_term_fails(
    perovskite_term,
    tmd_term,
    photo_term,
):
    with pytest.raises(
        ValueError,
        match="all be non-empty",
    ):
        build_query_text(
            perovskite_term,
            tmd_term,
            photo_term,
        )


# ---------------------------------------------------------------------------
# BUILD QUERY FAMILY
# ---------------------------------------------------------------------------
def test_build_query_family():
    queries = (
        build_query_family(
            family="test_family",
            perovskite_terms=(
                "CaTiO3",
                "LaCoO3",
            ),
            tmd_terms=(
                "MoS2",
            ),
            photo_terms=(
                "photocatalysis",
                "hydrogen evolution",
            ),
        )
    )

    assert len(
        queries
    ) == 4

    assert all(
        isinstance(
            query,
            DiscoveryQuery,
        )
        for query in queries
    )

    assert (
        queries[
            0
        ].query_id
        == "QRY-000001"
    )

    assert (
        queries[
            -1
        ].query_id
        == "QRY-000004"
    )

    assert (
        queries[
            0
        ].family
        == "test_family"
    )


# ---------------------------------------------------------------------------
# QUERY FAMILY ORDER IS DETERMINISTIC
# ---------------------------------------------------------------------------
def test_query_family_order_is_deterministic():
    queries = (
        build_query_family(
            family="test_family",
            perovskite_terms=(
                "CaTiO3",
                "LaCoO3",
            ),
            tmd_terms=(
                "MoS2",
                "WS2",
            ),
            photo_terms=(
                "photocatalysis",
            ),
        )
    )

    assert [
        query.query_text
        for query in queries
    ] == [
        (
            "CaTiO3 MoS2 "
            "photocatalysis"
        ),
        (
            "CaTiO3 WS2 "
            "photocatalysis"
        ),
        (
            "LaCoO3 MoS2 "
            "photocatalysis"
        ),
        (
            "LaCoO3 WS2 "
            "photocatalysis"
        ),
    ]


# ---------------------------------------------------------------------------
# QUERY FAMILY DEDUPLICATES TEXT
# ---------------------------------------------------------------------------
def test_query_family_deduplicates_text():
    queries = (
        build_query_family(
            family="test_family",
            perovskite_terms=(
                "CaTiO3",
                "  CaTiO3  ",
            ),
            tmd_terms=(
                "MoS2",
            ),
            photo_terms=(
                "photocatalysis",
            ),
        )
    )

    assert len(
        queries
    ) == 1

    assert (
        queries[
            0
        ].query_text
        == (
            "CaTiO3 MoS2 "
            "photocatalysis"
        )
    )


# ---------------------------------------------------------------------------
# INVALID QUERY FAMILY FAILS
# ---------------------------------------------------------------------------
def test_empty_query_family_fails():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        build_query_family(
            family="   ",
            perovskite_terms=(
                "CaTiO3",
            ),
            tmd_terms=(
                "MoS2",
            ),
            photo_terms=(
                "photocatalysis",
            ),
        )


# ---------------------------------------------------------------------------
# INVALID START INDEX FAILS
# ---------------------------------------------------------------------------
def test_invalid_start_index_fails():
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        build_query_family(
            family="test_family",
            perovskite_terms=(
                "CaTiO3",
            ),
            tmd_terms=(
                "MoS2",
            ),
            photo_terms=(
                "photocatalysis",
            ),
            start_index=0,
        )


# ---------------------------------------------------------------------------
# DEFAULT DISCOVERY QUERY COUNT
# ---------------------------------------------------------------------------
def test_default_discovery_query_count():
    queries = (
        build_default_discovery_queries()
    )

    assert len(
        queries
    ) == 616


# ---------------------------------------------------------------------------
# DEFAULT QUERY IDS ARE UNIQUE
# ---------------------------------------------------------------------------
def test_default_query_ids_are_unique():
    queries = (
        build_default_discovery_queries()
    )

    query_ids = [
        query.query_id
        for query in queries
    ]

    assert (
        len(
            query_ids
        )
        == len(
            set(
                query_ids
            )
        )
    )


# ---------------------------------------------------------------------------
# DEFAULT QUERY TEXTS ARE UNIQUE
# ---------------------------------------------------------------------------
def test_default_query_texts_are_unique():
    queries = (
        build_default_discovery_queries()
    )

    query_texts = [
        query.query_text.casefold()
        for query in queries
    ]

    assert (
        len(
            query_texts
        )
        == len(
            set(
                query_texts
            )
        )
    )


# ---------------------------------------------------------------------------
# DEFAULT QUERY FAMILIES EXIST
# ---------------------------------------------------------------------------
def test_default_query_families_exist():
    queries = (
        build_default_discovery_queries()
    )

    families = {
        query.family
        for query in queries
    }

    assert families == {
        "generic_perovskite",
        "seed_perovskite",
    }


# ---------------------------------------------------------------------------
# KNOWN TARGET QUERY EXISTS
# ---------------------------------------------------------------------------
def test_known_target_query_exists():
    queries = (
        build_default_discovery_queries()
    )

    query_texts = {
        query.query_text
        for query in queries
    }

    assert (
        "LaCoO3 MoS2 photocatalysis"
        in query_texts
    )

    assert (
        "CaTiO3 WS2 hydrogen evolution"
        in query_texts
    )

