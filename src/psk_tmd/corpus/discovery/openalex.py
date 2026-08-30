import json

from typing import Any
from urllib.parse import (
    urlencode,
)
from urllib.request import (
    Request,
    urlopen,
)

from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
    normalize_doi,
)


# ---------------------------------------------------------------------------
# OPENALEX CONFIGURATION
# ---------------------------------------------------------------------------
OPENALEX_API_URL = (
    "https://api.openalex.org/works"
)

OPENALEX_SOURCE = "openalex"

DEFAULT_PER_PAGE = 20

DEFAULT_USER_AGENT = (
    "psk-tmd-ml/0.1 "
    "(academic research)"
)


# ---------------------------------------------------------------------------
# GET OPENALEX DOI
# ---------------------------------------------------------------------------
def get_openalex_doi(
    item: dict[
        str,
        Any,
    ],
) -> str | None:
    doi = item.get(
        "doi"
    )

    if not isinstance(
        doi,
        str,
    ):
        return None

    return normalize_doi(
        doi
    )


# ---------------------------------------------------------------------------
# GET OPENALEX AUTHORS
# ---------------------------------------------------------------------------
def get_openalex_authors(
    item: dict[
        str,
        Any,
    ],
) -> list[
    str
]:
    authorships = item.get(
        "authorships"
    )

    if not isinstance(
        authorships,
        list,
    ):
        return []

    authors: list[
        str
    ] = []

    for authorship in authorships:
        if not isinstance(
            authorship,
            dict,
        ):
            continue

        author = authorship.get(
            "author"
        )

        if not isinstance(
            author,
            dict,
        ):
            continue

        display_name = author.get(
            "display_name"
        )

        if not isinstance(
            display_name,
            str,
        ):
            continue

        normalized = " ".join(
            display_name.split()
        )

        if (
            normalized
            and normalized
            not in authors
        ):
            authors.append(
                normalized
            )

    return authors


# ---------------------------------------------------------------------------
# GET OPENALEX JOURNAL
# ---------------------------------------------------------------------------
def get_openalex_journal(
    item: dict[
        str,
        Any,
    ],
) -> str | None:
    primary_location = item.get(
        "primary_location"
    )

    if not isinstance(
        primary_location,
        dict,
    ):
        return None

    source = primary_location.get(
        "source"
    )

    if not isinstance(
        source,
        dict,
    ):
        return None

    display_name = source.get(
        "display_name"
    )

    if not isinstance(
        display_name,
        str,
    ):
        return None

    normalized = " ".join(
        display_name.split()
    )

    if not normalized:
        return None

    return normalized


# ---------------------------------------------------------------------------
# GET OPENALEX PUBLISHER
# ---------------------------------------------------------------------------
def get_openalex_publisher(
    item: dict[
        str,
        Any,
    ],
) -> str | None:
    primary_location = item.get(
        "primary_location"
    )

    if not isinstance(
        primary_location,
        dict,
    ):
        return None

    source = primary_location.get(
        "source"
    )

    if not isinstance(
        source,
        dict,
    ):
        return None

    host_organization_name = source.get(
        "host_organization_name"
    )

    if not isinstance(
        host_organization_name,
        str,
    ):
        return None

    normalized = " ".join(
        host_organization_name.split()
    )

    if not normalized:
        return None

    return normalized


# ---------------------------------------------------------------------------
# RECONSTRUCT OPENALEX ABSTRACT
# ---------------------------------------------------------------------------
def reconstruct_openalex_abstract(
    inverted_index: Any,
) -> str | None:
    if not isinstance(
        inverted_index,
        dict,
    ):
        return None

    positioned_words: list[
        tuple[
            int,
            str,
        ]
    ] = []

    for (
        word,
        positions,
    ) in inverted_index.items():
        if (
            not isinstance(
                word,
                str,
            )
            or not isinstance(
                positions,
                list,
            )
        ):
            continue

        for position in positions:
            if not isinstance(
                position,
                int,
            ):
                continue

            positioned_words.append(
                (
                    position,
                    word,
                )
            )

    if not positioned_words:
        return None

    positioned_words.sort(
        key=lambda item: item[
            0
        ]
    )

    return " ".join(
        word
        for (
            _,
            word,
        ) in positioned_words
    )


# ---------------------------------------------------------------------------
# GET OPENALEX OA STATUS
# ---------------------------------------------------------------------------
def get_openalex_oa_status(
    item: dict[
        str,
        Any,
    ],
) -> bool | None:
    open_access = item.get(
        "open_access"
    )

    if not isinstance(
        open_access,
        dict,
    ):
        return None

    is_oa = open_access.get(
        "is_oa"
    )

    if isinstance(
        is_oa,
        bool,
    ):
        return is_oa

    return None


# ---------------------------------------------------------------------------
# GET OPENALEX LANDING PAGE
# ---------------------------------------------------------------------------
def get_openalex_landing_page(
    item: dict[
        str,
        Any,
    ],
) -> str | None:
    primary_location = item.get(
        "primary_location"
    )

    if not isinstance(
        primary_location,
        dict,
    ):
        return None

    landing_page_url = (
        primary_location.get(
            "landing_page_url"
        )
    )

    if not isinstance(
        landing_page_url,
        str,
    ):
        return None

    return landing_page_url


# ---------------------------------------------------------------------------
# BUILD OPENALEX DISCOVERY RECORD
# ---------------------------------------------------------------------------
def build_openalex_discovery_record(
    item: dict[
        str,
        Any,
    ],
    *,
    discovery_id: str,
) -> DiscoveryRecord:
    title = item.get(
        "title"
    )

    if (
        not isinstance(
            title,
            str,
        )
        or not title.strip()
    ):
        raise ValueError(
            "OpenAlex item is missing "
            "a usable title."
        )

    source_id = item.get(
        "id"
    )

    if not isinstance(
        source_id,
        str,
    ):
        source_id = None

    publication_year = item.get(
        "publication_year"
    )

    if not isinstance(
        publication_year,
        int,
    ):
        publication_year = None

    return DiscoveryRecord(
        discovery_id=discovery_id,
        doi=(
            get_openalex_doi(
                item
            )
        ),
        title=title,
        authors=(
            get_openalex_authors(
                item
            )
        ),
        year=publication_year,
        journal=(
            get_openalex_journal(
                item
            )
        ),
        publisher=(
            get_openalex_publisher(
                item
            )
        ),
        abstract=(
            reconstruct_openalex_abstract(
                item.get(
                    "abstract_inverted_index"
                )
            )
        ),
        source=OPENALEX_SOURCE,
        source_id=source_id,
        is_open_access=(
            get_openalex_oa_status(
                item
            )
        ),
        landing_page_url=(
            get_openalex_landing_page(
                item
            )
        ),
    )


# ---------------------------------------------------------------------------
# BUILD OPENALEX DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def build_openalex_discovery_records(
    items: list[
        dict[
            str,
            Any,
        ]
    ],
    *,
    start_index: int = 1,
) -> list[
    DiscoveryRecord
]:
    records: list[
        DiscoveryRecord
    ] = []

    next_index = start_index

    for item in items:
        try:
            record = (
                build_openalex_discovery_record(
                    item,
                    discovery_id=(
                        f"DSC-{next_index:06d}"
                    ),
                )
            )
        except ValueError:
            continue

        records.append(
            record
        )

        next_index += 1

    return records


# ---------------------------------------------------------------------------
# BUILD OPENALEX URL
# ---------------------------------------------------------------------------
def build_openalex_url(
    query: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    api_key: str | None = None,
) -> str:
    if not query.strip():
        raise ValueError(
            "OpenAlex query must not "
            "be empty."
        )

    if (
        per_page < 1
        or per_page > 100
    ):
        raise ValueError(
            "OpenAlex per_page must be "
            "between 1 and 100."
        )

    parameters = {
        "search": query.strip(),
        "filter": "type:article",
        "per-page": per_page,
    }

    if (
        api_key is not None
        and api_key.strip()
    ):
        parameters[
            "api_key"
        ] = api_key.strip()

    return (
        f"{OPENALEX_API_URL}?"
        f"{urlencode(parameters)}"
    )


# ---------------------------------------------------------------------------
# FETCH OPENALEX ITEMS
# ---------------------------------------------------------------------------
def fetch_openalex_items(
    query: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    api_key: str | None = None,
    user_agent: str = (
        DEFAULT_USER_AGENT
    ),
    timeout: float = 30.0,
) -> list[
    dict[
        str,
        Any,
    ]
]:
    url = build_openalex_url(
        query,
        per_page=per_page,
        api_key=api_key,
    )

    request = Request(
        url,
        headers={
            "Accept": (
                "application/json"
            ),
            "User-Agent": (
                user_agent
            ),
        },
    )

    with urlopen(
        request,
        timeout=timeout,
    ) as response:
        payload = json.load(
            response
        )

    results = payload.get(
        "results"
    )

    if not isinstance(
        results,
        list,
    ):
        raise ValueError(
            "OpenAlex response is missing "
            "the results list."
        )

    return [
        item
        for item in results
        if isinstance(
            item,
            dict,
        )
    ]


# ---------------------------------------------------------------------------
# DISCOVER OPENALEX RECORDS
# ---------------------------------------------------------------------------
def discover_openalex_records(
    query: str,
    *,
    per_page: int = DEFAULT_PER_PAGE,
    api_key: str | None = None,
    start_index: int = 1,
) -> list[
    DiscoveryRecord
]:
    items = fetch_openalex_items(
        query,
        per_page=per_page,
        api_key=api_key,
    )

    return (
        build_openalex_discovery_records(
            items,
            start_index=start_index,
        )
    )


