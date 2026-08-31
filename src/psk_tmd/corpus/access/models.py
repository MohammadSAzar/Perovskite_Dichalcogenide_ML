from datetime import (
    date,
)
from enum import (
    Enum,
)

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# ACCESS STATUS
# ---------------------------------------------------------------------------
class AccessStatus(
    str,
    Enum,
):
    AVAILABLE = "available"
    METADATA_ONLY = "metadata_only"
    REQUIRES_REVIEW = "requires_review"
    UNAVAILABLE = "unavailable"


# ---------------------------------------------------------------------------
# ACQUISITION ROUTE
# ---------------------------------------------------------------------------
class AcquisitionRoute(
    str,
    Enum,
):
    OFFICIAL_API = "official_api"
    OA_REPOSITORY = "oa_repository"
    CROSSREF_TDM = "crossref_tdm"
    AUTHOR_REPOSITORY = "author_repository"
    PUBLISHER_DOWNLOAD = "publisher_download"
    CONTROLLED_CRAWLING = "controlled_crawling"
    NONE = "none"


# ---------------------------------------------------------------------------
# TDM STATUS
# ---------------------------------------------------------------------------
class TDMStatus(
    str,
    Enum,
):
    PERMITTED = "permitted"
    NOT_PERMITTED = "not_permitted"
    UNCLEAR = "unclear"
    NOT_EVALUATED = "not_evaluated"


# ---------------------------------------------------------------------------
# FULL TEXT FORMAT
# ---------------------------------------------------------------------------
class FullTextFormat(
    str,
    Enum,
):
    XML = "xml"
    HTML = "html"
    PDF = "pdf"
    TEXT = "text"


# ---------------------------------------------------------------------------
# ACCESS RECORD
# ---------------------------------------------------------------------------
class AccessRecord(
    BaseModel
):
    access_id: str

    candidate_id: str

    doi: str | None = None

    publisher: str | None = None

    is_open_access: bool | None = None

    oa_status: str | None = None

    license: str | None = None

    license_url: str | None = None

    access_status: AccessStatus = (
        AccessStatus.REQUIRES_REVIEW
    )

    acquisition_route: AcquisitionRoute = (
        AcquisitionRoute.NONE
    )

    source_url: str | None = None

    source_version: str | None = None

    tdm_status: TDMStatus = (
        TDMStatus.NOT_EVALUATED
    )

    tdm_basis: str | None = None

    full_text_available: bool = False

    full_text_format: FullTextFormat | None = None

    retrieval_date: date | None = None

    checksum: str | None = None

    notes: str | None = None

    @field_validator(
        "access_id",
        "candidate_id",
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
                "Required text field "
                "must not be empty."
            )

        return normalized

    @field_validator(
        "doi",
        "publisher",
        "oa_status",
        "license",
        "license_url",
        "source_url",
        "source_version",
        "tdm_basis",
        "checksum",
        "notes",
    )
    @classmethod
    def normalize_optional_text(
        cls,
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

    @field_validator(
        "doi",
    )
    @classmethod
    def normalize_doi(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = (
            value
            .strip()
            .lower()
        )

        prefixes = (
            "https://doi.org/",
            "http://doi.org/",
            "https://dx.doi.org/",
            "http://dx.doi.org/",
            "doi:",
        )

        for prefix in prefixes:
            if normalized.startswith(
                prefix
            ):
                normalized = (
                    normalized[
                        len(
                            prefix
                        ):
                    ]
                    .strip()
                )

                break

        return (
            normalized
            or None
        )

    @field_validator(
        "full_text_format",
    )
    @classmethod
    def validate_full_text_format(
        cls,
        value: FullTextFormat | None,
        info,
    ) -> FullTextFormat | None:
        if (
            value is not None
            and not info.data.get(
                "full_text_available",
                False,
            )
        ):
            raise ValueError(
                "full_text_format requires "
                "full_text_available=True."
            )

        return value

