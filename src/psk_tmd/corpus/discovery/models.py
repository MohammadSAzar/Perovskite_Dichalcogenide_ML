from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# NORMALIZE OPTIONAL TEXT
# ---------------------------------------------------------------------------
def normalize_optional_text(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    normalized = (
        normalize_whitespace(
            value
        )
    )

    if not normalized:
        return None

    return normalized


# ---------------------------------------------------------------------------
# NORMALIZE DOI
# ---------------------------------------------------------------------------
def normalize_doi(
    value: str | None,
) -> str | None:
    normalized = (
        normalize_optional_text(
            value
        )
    )

    if normalized is None:
        return None

    lowered = normalized.lower()

    prefixes = (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    )

    for prefix in prefixes:
        if lowered.startswith(
            prefix
        ):
            normalized = (
                normalized[
                    len(prefix):
                ]
                .strip()
            )
            break

    if not normalized:
        return None

    return normalized.lower()


# ---------------------------------------------------------------------------
# DISCOVERY RECORD
# ---------------------------------------------------------------------------
class DiscoveryRecord(BaseModel):
    discovery_id: str

    doi: str | None = None

    title: str

    authors: list[
        str
    ] = Field(
        default_factory=list
    )

    year: int | None = Field(
        default=None,
        ge=1000,
    )

    journal: str | None = None

    publisher: str | None = None

    abstract: str | None = None

    source: str

    source_id: str | None = None

    is_open_access: bool | None = None

    landing_page_url: str | None = None

    # -----------------------------------------------------------------------
    # REQUIRED TEXT
    # -----------------------------------------------------------------------
    @field_validator(
        "discovery_id",
        "title",
        "source",
    )
    @classmethod
    def validate_required_text(
        cls,
        value: str,
    ) -> str:
        normalized = (
            normalize_whitespace(
                value
            )
        )

        if not normalized:
            raise ValueError(
                "Value must not be empty."
            )

        return normalized

    # -----------------------------------------------------------------------
    # DOI
    # -----------------------------------------------------------------------
    @field_validator(
        "doi",
    )
    @classmethod
    def validate_doi(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_doi(
            value
        )

    # -----------------------------------------------------------------------
    # AUTHORS
    # -----------------------------------------------------------------------
    @field_validator(
        "authors",
    )
    @classmethod
    def validate_authors(
        cls,
        value: list[
            str
        ],
    ) -> list[
        str
    ]:
        normalized_authors: list[
            str
        ] = []

        for author in value:
            normalized = (
                normalize_whitespace(
                    author
                )
            )

            if not normalized:
                continue

            normalized_authors.append(
                normalized
            )

        return normalized_authors

    # -----------------------------------------------------------------------
    # OPTIONAL TEXT
    # -----------------------------------------------------------------------
    @field_validator(
        "journal",
        "publisher",
        "abstract",
        "source_id",
        "landing_page_url",
    )
    @classmethod
    def validate_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        return normalize_optional_text(
            value
        )

