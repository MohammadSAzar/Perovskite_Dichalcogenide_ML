import time

from dataclasses import (
    dataclass,
)
from typing import (
    Callable,
)

from psk_tmd.corpus.discovery.crossref import (
    discover_crossref_records,
)
from psk_tmd.corpus.discovery.execution_plan import (
    QueryExecutionItem,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.openalex import (
    discover_openalex_records,
)


# ---------------------------------------------------------------------------
# DISCOVERY HIT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryHit:
    query_id: str

    query_text: str

    family: str

    source: str

    source_rank: int

    record: DiscoveryRecord


# ---------------------------------------------------------------------------
# DISCOVERY RUN RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryRunResult:
    hits: tuple[
        DiscoveryHit,
        ...
    ]

    attempted_calls: int

    successful_calls: int

    failed_calls: int


# ---------------------------------------------------------------------------
# SOURCE FETCHER TYPE
# ---------------------------------------------------------------------------
SourceFetcher = Callable[
    [
        str,
        int,
    ],
    list[
        DiscoveryRecord
    ],
]


# ---------------------------------------------------------------------------
# FETCH CROSSREF RECORDS
# ---------------------------------------------------------------------------
def fetch_crossref_records(
    query_text: str,
    result_limit: int,
) -> list[
    DiscoveryRecord
]:
    return (
        discover_crossref_records(
            query_text,
            rows=result_limit,
        )
    )


# ---------------------------------------------------------------------------
# FETCH OPENALEX RECORDS
# ---------------------------------------------------------------------------
def fetch_openalex_records(
    query_text: str,
    result_limit: int,
) -> list[
    DiscoveryRecord
]:
    return (
        discover_openalex_records(
            query_text,
            per_page=result_limit,
        )
    )


# ---------------------------------------------------------------------------
# GET SOURCE FETCHERS
# ---------------------------------------------------------------------------
def get_source_fetchers(
) -> dict[
    str,
    SourceFetcher,
]:
    return {
        "crossref": (
            fetch_crossref_records
        ),
        "openalex": (
            fetch_openalex_records
        ),
    }


# ---------------------------------------------------------------------------
# BUILD DISCOVERY HITS
# ---------------------------------------------------------------------------
def build_discovery_hits(
    *,
    item: QueryExecutionItem,
    source: str,
    records: list[
        DiscoveryRecord
    ],
) -> list[
    DiscoveryHit
]:
    return [
        DiscoveryHit(
            query_id=(
                item.query_id
            ),
            query_text=(
                item.query_text
            ),
            family=(
                item.family
            ),
            source=source,
            source_rank=rank,
            record=record,
        )
        for (
            rank,
            record,
        ) in enumerate(
            records,
            start=1,
        )
    ]


# ---------------------------------------------------------------------------
# RUN DISCOVERY PLAN
# ---------------------------------------------------------------------------
def run_discovery_plan(
    plan: list[
        QueryExecutionItem
    ],
    *,
    result_limit: int = 10,
    delay_seconds: float = 0.5,
    source_fetchers: dict[
        str,
        SourceFetcher,
    ] | None = None,
) -> DiscoveryRunResult:
    if result_limit < 1:
        raise ValueError(
            "Discovery result_limit must "
            "be at least 1."
        )

    if delay_seconds < 0.0:
        raise ValueError(
            "Discovery delay_seconds must "
            "not be negative."
        )

    fetchers = (
        source_fetchers
        if source_fetchers
        is not None
        else get_source_fetchers()
    )

    hits: list[
        DiscoveryHit
    ] = []

    attempted_calls = 0
    successful_calls = 0
    failed_calls = 0

    for item in plan:
        for source in item.sources:
            attempted_calls += 1

            fetcher = fetchers.get(
                source
            )

            if fetcher is None:
                failed_calls += 1
                continue

            try:
                records = fetcher(
                    item.query_text,
                    result_limit,
                )
            except Exception:
                failed_calls += 1

            else:
                successful_calls += 1

                hits.extend(
                    build_discovery_hits(
                        item=item,
                        source=source,
                        records=records,
                    )
                )

            if delay_seconds > 0.0:
                time.sleep(
                    delay_seconds
                )

    return DiscoveryRunResult(
        hits=tuple(
            hits
        ),
        attempted_calls=(
            attempted_calls
        ),
        successful_calls=(
            successful_calls
        ),
        failed_calls=(
            failed_calls
        ),
    )

