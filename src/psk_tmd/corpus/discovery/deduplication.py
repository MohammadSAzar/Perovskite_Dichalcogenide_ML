from collections import (
    defaultdict,
)

from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)


# ---------------------------------------------------------------------------
# NORMALIZE TITLE KEY
# ---------------------------------------------------------------------------
def normalize_title_key(
    title: str,
) -> str:
    return "".join(
        character.lower()
        for character in title
        if character.isalnum()
    )


# ---------------------------------------------------------------------------
# GET DOI GROUP KEY
# ---------------------------------------------------------------------------
def get_doi_group_key(
    record: DiscoveryRecord,
) -> str | None:
    if record.doi is None:
        return None

    return (
        f"doi:{record.doi}"
    )


# ---------------------------------------------------------------------------
# GET TITLE GROUP KEY
# ---------------------------------------------------------------------------
def get_title_group_key(
    record: DiscoveryRecord,
) -> str:
    normalized_title = (
        normalize_title_key(
            record.title
        )
    )

    return (
        f"title:{normalized_title}"
    )


# ---------------------------------------------------------------------------
# GET DISCOVERY GROUP KEY
# ---------------------------------------------------------------------------
def get_discovery_group_key(
    record: DiscoveryRecord,
) -> str:
    doi_key = (
        get_doi_group_key(
            record
        )
    )

    if doi_key is not None:
        return doi_key

    return (
        get_title_group_key(
            record
        )
    )


# ---------------------------------------------------------------------------
# GROUP DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def group_discovery_records(
    records: list[
        DiscoveryRecord
    ],
) -> dict[
    str,
    list[
        DiscoveryRecord
    ],
]:
    grouped: dict[
        str,
        list[
            DiscoveryRecord
        ],
    ] = defaultdict(
        list
    )

    for record in records:
        key = (
            get_discovery_group_key(
                record
            )
        )

        grouped[
            key
        ].append(
            record
        )

    return dict(
        grouped
    )


# ---------------------------------------------------------------------------
# SELECT PREFERRED TEXT
# ---------------------------------------------------------------------------
def select_preferred_text(
    values: list[
        str | None
    ],
) -> str | None:
    candidates = [
        value
        for value in values
        if (
            value is not None
            and value.strip()
        )
    ]

    if not candidates:
        return None

    return max(
        candidates,
        key=len,
    )


# ---------------------------------------------------------------------------
# MERGE AUTHORS
# ---------------------------------------------------------------------------
def merge_authors(
    records: list[
        DiscoveryRecord
    ],
) -> list[
    str
]:
    authors: list[
        str
    ] = []

    for record in records:
        for author in record.authors:
            if author not in authors:
                authors.append(
                    author
                )

    return authors


# ---------------------------------------------------------------------------
# SELECT YEAR
# ---------------------------------------------------------------------------
def select_year(
    records: list[
        DiscoveryRecord
    ],
) -> int | None:
    years = [
        record.year
        for record in records
        if record.year
        is not None
    ]

    if not years:
        return None

    return min(
        years
    )


# ---------------------------------------------------------------------------
# SELECT OPEN ACCESS STATUS
# ---------------------------------------------------------------------------
def select_open_access_status(
    records: list[
        DiscoveryRecord
    ],
) -> bool | None:
    values = [
        record.is_open_access
        for record in records
        if record.is_open_access
        is not None
    ]

    if not values:
        return None

    if True in values:
        return True

    return False


# ---------------------------------------------------------------------------
# MERGE DISCOVERY GROUP
# ---------------------------------------------------------------------------
def merge_discovery_group(
    records: list[
        DiscoveryRecord
    ],
    *,
    discovery_id: str,
) -> DiscoveryRecord:
    if not records:
        raise ValueError(
            "Discovery record group "
            "must not be empty."
        )

    doi_values = {
        record.doi
        for record in records
        if record.doi
        is not None
    }

    if len(
        doi_values
    ) > 1:
        raise ValueError(
            "Discovery record group "
            "contains conflicting DOIs."
        )

    doi = (
        next(
            iter(
                doi_values
            )
        )
        if doi_values
        else None
    )

    title = (
        select_preferred_text(
            [
                record.title
                for record in records
            ]
        )
    )

    if title is None:
        raise ValueError(
            "Merged discovery record "
            "requires a title."
        )

    sources = sorted(
        {
            record.source
            for record in records
        }
    )

    source_ids = sorted(
        {
            record.source_id
            for record in records
            if record.source_id
            is not None
        }
    )

    return DiscoveryRecord(
        discovery_id=discovery_id,
        doi=doi,
        title=title,
        authors=(
            merge_authors(
                records
            )
        ),
        year=(
            select_year(
                records
            )
        ),
        journal=(
            select_preferred_text(
                [
                    record.journal
                    for record
                    in records
                ]
            )
        ),
        publisher=(
            select_preferred_text(
                [
                    record.publisher
                    for record
                    in records
                ]
            )
        ),
        abstract=(
            select_preferred_text(
                [
                    record.abstract
                    for record
                    in records
                ]
            )
        ),
        source="+".join(
            sources
        ),
        source_id=(
            ";".join(
                source_ids
            )
            if source_ids
            else None
        ),
        is_open_access=(
            select_open_access_status(
                records
            )
        ),
        landing_page_url=(
            select_preferred_text(
                [
                    record.landing_page_url
                    for record
                    in records
                ]
            )
        ),
    )


# ---------------------------------------------------------------------------
# DEDUPLICATE DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def deduplicate_discovery_records(
    records: list[
        DiscoveryRecord
    ],
    *,
    start_index: int = 1,
) -> list[
    DiscoveryRecord
]:
    grouped = (
        group_discovery_records(
            records
        )
    )

    merged_records: list[
        DiscoveryRecord
    ] = []

    next_index = (
        start_index
    )

    for key in sorted(
        grouped
    ):
        merged = (
            merge_discovery_group(
                grouped[
                    key
                ],
                discovery_id=(
                    f"DSC-{next_index:06d}"
                ),
            )
        )

        merged_records.append(
            merged
        )

        next_index += 1

    return merged_records

