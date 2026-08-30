import html
import json
import re

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
# CROSSREF CONFIGURATION
# ---------------------------------------------------------------------------
CROSSREF_API_URL = (
    "https://api.crossref.org/works"
)

CROSSREF_SOURCE = "crossref"

DEFAULT_ROWS = 20

DEFAULT_USER_AGENT = (
    "psk-tmd-ml/0.1 "
    "(academic research)"
)


# ---------------------------------------------------------------------------
# CLEAN CROSSREF ABSTRACT
# ---------------------------------------------------------------------------
def clean_crossref_abstract(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    cleaned = re.sub(
        r"<[^>]+>",
        " ",
        value,
    )

    cleaned = html.unescape(
        cleaned
    )

    cleaned = " ".join(
        cleaned.split()
    )

    if not cleaned:
        return None

    return cleaned


# ---------------------------------------------------------------------------
# GET FIRST TEXT VALUE
# ---------------------------------------------------------------------------
def get_first_text_value(
    value: Any,
) -> str | None:
    if not isinstance(
        value,
        list,
    ):
        return None

    for item in value:
        if not isinstance(
            item,
            str,
        ):
            continue

        normalized = " ".join(
            item.split()
        )

        if normalized:
            return normalized

    return None


# ---------------------------------------------------------------------------
# GET CROSSREF YEAR
# ---------------------------------------------------------------------------
def get_crossref_year(
    item: dict[
        str,
        Any,
    ],
) -> int | None:
    date_fields = (
        "published-print",
        "published-online",
        "published",
        "issued",
    )

    for field_name in date_fields:
        value = item.get(
            field_name
        )

        if not isinstance(
            value,
            dict,
        ):
            continue

        date_parts = value.get(
            "date-parts"
        )

        if (
            not isinstance(
                date_parts,
                list,
            )
            or not date_parts
        ):
            continue

        first_date = date_parts[
            0
        ]

        if (
            not isinstance(
                first_date,
                list,
            )
            or not first_date
        ):
            continue

        year = first_date[
            0
        ]

        if isinstance(
            year,
            int,
        ):
            return year

    return None


# ---------------------------------------------------------------------------
# FORMAT CROSSREF AUTHOR
# ---------------------------------------------------------------------------
def format_crossref_author(
    author: dict[
        str,
        Any,
    ],
) -> str | None:
    given = author.get(
        "given"
    )

    family = author.get(
        "family"
    )

    parts = [
        str(
            value
        ).strip()
        for value in (
            given,
            family,
        )
        if (
            value is not None
            and str(
                value
            ).strip()
        )
    ]

    if not parts:
        name = author.get(
            "name"
        )

        if (
            isinstance(
                name,
                str,
            )
            and name.strip()
        ):
            return " ".join(
                name.split()
            )

        return None

    return " ".join(
        parts
    )


# ---------------------------------------------------------------------------
# GET CROSSREF AUTHORS
# ---------------------------------------------------------------------------
def get_crossref_authors(
    item: dict[
        str,
        Any,
    ],
) -> list[
    str
]:
    raw_authors = item.get(
        "author"
    )

    if not isinstance(
        raw_authors,
        list,
    ):
        return []

    authors: list[
        str
    ] = []

    for raw_author in raw_authors:
        if not isinstance(
            raw_author,
            dict,
        ):
            continue

        author = (
            format_crossref_author(
                raw_author
            )
        )

        if (
            author is not None
            and author
            not in authors
        ):
            authors.append(
                author
            )

    return authors


# ---------------------------------------------------------------------------
# BUILD CROSSREF DISCOVERY RECORD
# ---------------------------------------------------------------------------
def build_crossref_discovery_record(
    item: dict[
        str,
        Any,
    ],
    *,
    discovery_id: str,
) -> DiscoveryRecord:
    title = get_first_text_value(
        item.get(
            "title"
        )
    )

    if title is None:
        raise ValueError(
            "Crossref item is missing "
            "a usable title."
        )

    doi = normalize_doi(
        item.get(
            "DOI"
        )
    )

    source_id = doi

    journal = get_first_text_value(
        item.get(
            "container-title"
        )
    )

    publisher = item.get(
        "publisher"
    )

    if not isinstance(
        publisher,
        str,
    ):
        publisher = None

    landing_page_url = item.get(
        "URL"
    )

    if not isinstance(
        landing_page_url,
        str,
    ):
        landing_page_url = None

    abstract = (
        clean_crossref_abstract(
            item.get(
                "abstract"
            )
            if isinstance(
                item.get(
                    "abstract"
                ),
                str,
            )
            else None
        )
    )

    return DiscoveryRecord(
        discovery_id=discovery_id,
        doi=doi,
        title=title,
        authors=(
            get_crossref_authors(
                item
            )
        ),
        year=(
            get_crossref_year(
                item
            )
        ),
        journal=journal,
        publisher=publisher,
        abstract=abstract,
        source=CROSSREF_SOURCE,
        source_id=source_id,
        is_open_access=None,
        landing_page_url=(
            landing_page_url
        ),
    )


# ---------------------------------------------------------------------------
# BUILD CROSSREF DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def build_crossref_discovery_records(
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
                build_crossref_discovery_record(
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
# BUILD CROSSREF URL
# ---------------------------------------------------------------------------
def build_crossref_url(
    query: str,
    *,
    rows: int = DEFAULT_ROWS,
    mailto: str | None = None,
) -> str:
    if not query.strip():
        raise ValueError(
            "Crossref query must not "
            "be empty."
        )

    if rows < 1:
        raise ValueError(
            "Crossref rows must be "
            "at least 1."
        )

    parameters = {
        "query.bibliographic": (
            query.strip()
        ),
        "rows": rows,
    }

    if (
        mailto is not None
        and mailto.strip()
    ):
        parameters[
            "mailto"
        ] = mailto.strip()

    return (
        f"{CROSSREF_API_URL}?"
        f"{urlencode(parameters)}"
    )


# ---------------------------------------------------------------------------
# FETCH CROSSREF ITEMS
# ---------------------------------------------------------------------------
def fetch_crossref_items(
    query: str,
    *,
    rows: int = DEFAULT_ROWS,
    mailto: str | None = None,
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
    url = build_crossref_url(
        query,
        rows=rows,
        mailto=mailto,
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

    message = payload.get(
        "message"
    )

    if not isinstance(
        message,
        dict,
    ):
        raise ValueError(
            "Crossref response is missing "
            "the message object."
        )

    items = message.get(
        "items"
    )

    if not isinstance(
        items,
        list,
    ):
        raise ValueError(
            "Crossref response is missing "
            "the items list."
        )

    return [
        item
        for item in items
        if isinstance(
            item,
            dict,
        )
    ]


# ---------------------------------------------------------------------------
# DISCOVER CROSSREF RECORDS
# ---------------------------------------------------------------------------
def discover_crossref_records(
    query: str,
    *,
    rows: int = DEFAULT_ROWS,
    mailto: str | None = None,
    start_index: int = 1,
) -> list[
    DiscoveryRecord
]:
    items = fetch_crossref_items(
        query,
        rows=rows,
        mailto=mailto,
    )

    return (
        build_crossref_discovery_records(
            items,
            start_index=start_index,
        )
    )

