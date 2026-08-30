from psk_tmd.corpus.discovery.openalex import (
    discover_openalex_records,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    records = (
        discover_openalex_records(
            (
                "perovskite MoS2 "
                "photocatalysis"
            ),
            per_page=10,
        )
    )

    print(
        "OPENALEX DISCOVERY PREVIEW"
    )
    print(
        "=" * 110
    )

    for record in records:
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
            f"{record.discovery_id:<12} "
            f"{record.year!s:<6} "
            f"{oa_text:<8} "
            f"{record.doi or '-':<35} "
            f"{record.title[:65]}"
        )

    print(
        "-" * 110
    )
    print(
        f"records={len(records)}"
    )


if __name__ == "__main__":
    main()

