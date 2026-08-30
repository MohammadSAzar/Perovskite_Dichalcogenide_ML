from dataclasses import (
    dataclass,
)

from psk_tmd.corpus.discovery.query_strategy import (
    DiscoveryQuery,
)


# ---------------------------------------------------------------------------
# EXECUTION PLAN ITEM
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class QueryExecutionItem:
    execution_index: int

    query_id: str

    family: str

    query_text: str

    sources: tuple[
        str,
        ...
    ]


# ---------------------------------------------------------------------------
# PILOT VOCABULARY
# ---------------------------------------------------------------------------
PILOT_GENERIC_PEROVSKITE_TERMS = (
    "perovskite",
)

PILOT_SEED_PEROVSKITE_TERMS = (
    "CaTiO3",
    "SrTiO3",
    "PbTiO3",
    "LaFeO3",
    "LaCoO3",
    "LaNiO3",
    "BiFeO3",
)

PILOT_TMD_TERMS = (
    "MoS2",
    "WS2",
)

PILOT_PHOTO_TERMS = (
    "photocatalysis",
    "photocatalytic",
    "hydrogen evolution",
)

DEFAULT_DISCOVERY_SOURCES = (
    "crossref",
    "openalex",
)


# ---------------------------------------------------------------------------
# IS PILOT QUERY
# ---------------------------------------------------------------------------
def is_pilot_query(
    query: DiscoveryQuery,
) -> bool:
    if (
        query.tmd_term
        not in PILOT_TMD_TERMS
    ):
        return False

    if (
        query.photo_term
        not in PILOT_PHOTO_TERMS
    ):
        return False

    if (
        query.family
        == "generic_perovskite"
    ):
        return (
            query.perovskite_term
            in PILOT_GENERIC_PEROVSKITE_TERMS
        )

    if (
        query.family
        == "seed_perovskite"
    ):
        return (
            query.perovskite_term
            in PILOT_SEED_PEROVSKITE_TERMS
        )

    return False


# ---------------------------------------------------------------------------
# SELECT PILOT QUERIES
# ---------------------------------------------------------------------------
def select_pilot_queries(
    queries: list[
        DiscoveryQuery
    ],
) -> list[
    DiscoveryQuery
]:
    return [
        query
        for query in queries
        if is_pilot_query(
            query
        )
    ]


# ---------------------------------------------------------------------------
# BUILD EXECUTION PLAN
# ---------------------------------------------------------------------------
def build_execution_plan(
    queries: list[
        DiscoveryQuery
    ],
    *,
    sources: tuple[
        str,
        ...
    ] = DEFAULT_DISCOVERY_SOURCES,
) -> list[
    QueryExecutionItem
]:
    if not sources:
        raise ValueError(
            "Discovery execution sources "
            "must not be empty."
        )

    normalized_sources = tuple(
        source.strip().lower()
        for source in sources
        if source.strip()
    )

    if not normalized_sources:
        raise ValueError(
            "Discovery execution sources "
            "must not be empty."
        )

    if (
        len(
            normalized_sources
        )
        != len(
            set(
                normalized_sources
            )
        )
    ):
        raise ValueError(
            "Discovery execution sources "
            "must be unique."
        )

    items: list[
        QueryExecutionItem
    ] = []

    for index, query in enumerate(
        queries,
        start=1,
    ):
        items.append(
            QueryExecutionItem(
                execution_index=index,
                query_id=query.query_id,
                family=query.family,
                query_text=query.query_text,
                sources=normalized_sources,
            )
        )

    return items

