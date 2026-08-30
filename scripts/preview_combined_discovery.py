from psk_tmd.corpus.discovery.crossref import (
    discover_crossref_records,
)
from psk_tmd.corpus.discovery.deduplication import (
    deduplicate_discovery_records,
)
from psk_tmd.corpus.discovery.openalex import (
    discover_openalex_records,
)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    query = (
        "perovskite MoS2 "
        "photocatalysis"
    )

    crossref_records = (
        discover_crossref_records(
            query,
            rows=10,
            start_index=1,
        )
    )

    openalex_records = (
        discover_openalex_records(
            query,
            per_page=10,
            start_index=(
                len(
                    crossref_records
                )
                + 1
            ),
        )
    )

    combined_records = (
        crossref_records
        + openalex_records
    )

    merged_records = (
        deduplicate_discovery_records(
            combined_records
        )
    )

    crossref_dois = {
        record.doi
        for record
        in crossref_records
        if record.doi
        is not None
    }

    openalex_dois = {
        record.doi
        for record
        in openalex_records
        if record.doi
        is not None
    }

    duplicate_dois = (
        crossref_dois
        & openalex_dois
    )

    print(
        "COMBINED DISCOVERY PREVIEW"
    )
    print(
        "=" * 120
    )

    print(
        f"crossref_records="
        f"{len(crossref_records)}"
    )

    print(
        f"openalex_records="
        f"{len(openalex_records)}"
    )

    print(
        f"combined_raw="
        f"{len(combined_records)}"
    )

    print(
        f"duplicate_dois="
        f"{len(duplicate_dois)}"
    )

    print(
        f"merged_unique="
        f"{len(merged_records)}"
    )

    print()

    print(
        "DUPLICATE DOI MATCHES"
    )
    print(
        "-" * 120
    )

    if duplicate_dois:
        for doi in sorted(
            duplicate_dois
        ):
            print(
                doi
            )
    else:
        print(
            "None"
        )

    print()

    print(
        "MERGED RECORDS"
    )
    print(
        "-" * 120
    )

    for record in merged_records:
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
            f"{record.source:<20} "
            f"{record.doi or '-':<35} "
            f"{record.title[:55]}"
        )

    print(
        "-" * 120
    )


if __name__ == "__main__":
    main()

