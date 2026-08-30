from collections import (
    Counter,
)

from psk_tmd.corpus.discovery.query_strategy import (
    build_default_discovery_queries,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    queries = (
        build_default_discovery_queries()
    )

    family_counts = Counter(
        query.family
        for query in queries
    )

    print(
        "DISCOVERY QUERY STRATEGY"
    )
    print(
        "=" * 100
    )

    print(
        f"total_queries="
        f"{len(queries)}"
    )

    print()

    print(
        "QUERY FAMILIES"
    )
    print(
        "-" * 100
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
        "FIRST 20 QUERIES"
    )
    print(
        "-" * 100
    )

    for query in queries[
        :20
    ]:
        print(
            f"{query.query_id:<12} "
            f"{query.family:<25} "
            f"{query.query_text}"
        )

    print()

    print(
        "LAST 10 QUERIES"
    )
    print(
        "-" * 100
    )

    for query in queries[
        -10:
    ]:
        print(
            f"{query.query_id:<12} "
            f"{query.family:<25} "
            f"{query.query_text}"
        )


if __name__ == "__main__":
    main()

