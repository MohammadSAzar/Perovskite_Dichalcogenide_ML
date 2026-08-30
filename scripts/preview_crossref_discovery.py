from psk_tmd.corpus.discovery.crossref import (
    discover_crossref_records,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        discover_crossref_records(
            (
                "perovskite MoS2 "
                "photocatalysis"
            ),
            rows=10,
        )
    )

    print(
        "CROSSREF DISCOVERY PREVIEW"
    )
    print(
        "=" * 100
    )

    for record in records:
        print(
            f"{record.discovery_id:<12} "
            f"{record.year!s:<6} "
            f"{record.doi or '-':<35} "
            f"{record.title[:70]}"
        )

    print(
        "-" * 100
    )
    print(
        f"records={len(records)}"
    )


if __name__ == "__main__":
    main()

