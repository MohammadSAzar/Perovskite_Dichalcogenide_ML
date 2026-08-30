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

    plan = (
        build_execution_plan(
            pilot_queries
        )
    )

    family_counts = Counter(
        item.family
        for item in plan
    )

    total_source_calls = sum(
        len(
            item.sources
        )
        for item in plan
    )

    print(
        "DISCOVERY EXECUTION PLAN"
    )
    print(
        "=" * 110
    )

    print(
        f"available_queries="
        f"{len(all_queries)}"
    )

    print(
        f"selected_queries="
        f"{len(plan)}"
    )

    print(
        f"planned_source_calls="
        f"{total_source_calls}"
    )

    print()

    print(
        "SELECTED QUERY FAMILIES"
    )
    print(
        "-" * 110
    )

    for (
        family,
        count,
    ) in sorted(
        family_counts.items()
    ):
        print(
            f"{family:<25} "
            f"{count}"
        )

    print()

    print(
        "EXECUTION PLAN"
    )
    print(
        "-" * 110
    )

    for item in plan:
        print(
            f"{item.execution_index:>3}  "
            f"{item.query_id:<12} "
            f"{item.family:<22} "
            f"{','.join(item.sources):<20} "
            f"{item.query_text}"
        )

    print(
        "-" * 110
    )


if __name__ == "__main__":
    main()

