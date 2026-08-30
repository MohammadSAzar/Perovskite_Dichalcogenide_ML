from collections import (
    Counter,
)

from psk_tmd.corpus.discovery.execution_plan import (
    build_execution_plan,
    select_pilot_queries,
)
from psk_tmd.corpus.discovery.query_strategy import (
    build_default_discovery_queries,
)
from psk_tmd.corpus.discovery.runner import (
    run_discovery_plan,
)
from psk_tmd.corpus.discovery.candidates import (
    build_discovery_candidates,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    all_queries = (
        build_default_discovery_queries()
    )

    pilot_queries = (
        select_pilot_queries(
            all_queries
        )
    )

    full_plan = (
        build_execution_plan(
            pilot_queries
        )
    )

    test_plan = full_plan[
        :3
    ]

    result = (
        run_discovery_plan(
            test_plan,
            result_limit=5,
            delay_seconds=1.0,
        )
    )

    candidates = (
        build_discovery_candidates(
            result.hits
        )
    )

    source_counts = Counter(
        hit.source
        for hit in result.hits
    )

    query_counts = Counter(
        hit.query_id
        for hit in result.hits
    )

    print(
        "DISCOVERY RUNNER LIVE PREVIEW"
    )
    print(
        "=" * 130
    )

    print(
        f"selected_queries="
        f"{len(test_plan)}"
    )

    print(
        f"attempted_calls="
        f"{result.attempted_calls}"
    )

    print(
        f"successful_calls="
        f"{result.successful_calls}"
    )

    print(
        f"failed_calls="
        f"{result.failed_calls}"
    )

    print(
        f"raw_hits="
        f"{len(result.hits)}"
    )

    print()

    print(
        "UNIQUE DISCOVERY CANDIDATES"
    )
    print(
        "-" * 140
    )

    for candidate in candidates:
        record = (
            candidate.record
        )

        print(
            f"{candidate.candidate_id:<12} "
            f"hits={candidate.hit_count:<2} "
            f"queries={len(candidate.query_ids):<2} "
            f"sources={','.join(candidate.sources):<20} "
            f"{record.doi or '-':<35} "
            f"{record.title[:60]}"
        )

    print(
        "-" * 140
    )

    print(
        f"unique_candidates="
        f"{len(candidates)}"
    )

    print()

    print(
        "SOURCE COUNTS"
    )
    print(
        "-" * 130
    )

    for (
        source,
        count,
    ) in sorted(
        source_counts.items()
    ):
        print(
            f"{source:<15} "
            f"{count}"
        )

    print()

    print(
        "QUERY COUNTS"
    )
    print(
        "-" * 130
    )

    for item in test_plan:
        print(
            f"{item.query_id:<12} "
            f"{query_counts.get(item.query_id, 0):>3} "
            f"{item.query_text}"
        )

    print()

    print(
        "RAW DISCOVERY HITS"
    )
    print(
        "-" * 130
    )

    for hit in result.hits:
        record = (
            hit.record
        )

        oa_text = (
            "OA"
            if record.is_open_access
            is True
            else (
                "CLOSED"
                if record.is_open_access
                is False
                else "UNKNOWN"
            )
        )

        print(
            f"{hit.query_id:<12} "
            f"{hit.source:<10} "
            f"rank={hit.source_rank:<2} "
            f"{record.year!s:<6} "
            f"{oa_text:<8} "
            f"{record.doi or '-':<35} "
            f"{record.title[:55]}"
        )

    print(
        "-" * 130
    )


if __name__ == "__main__":
    main()

