from datetime import (
    date,
)
from enum import (
    Enum,
)

from pydantic import (
    BaseModel,
    field_validator,
)

from psk_tmd.common.text_utils import (
    normalize_whitespace,
)


# ---------------------------------------------------------------------------
# ACCESS EVIDENCE TYPE
# ---------------------------------------------------------------------------
class AccessEvidenceType(
    str,
    Enum,
):
    OA_STATUS = "oa_status"
    LICENSE = "license"
    FULL_TEXT_LOCATION = "full_text_location"
    TDM_PERMISSION = "tdm_permission"
    VERSION = "version"
    OTHER = "other"


# ---------------------------------------------------------------------------
# ACCESS EVIDENCE SOURCE
# ---------------------------------------------------------------------------
class AccessEvidenceSource(
    str,
    Enum,
):
    PUBLISHER = "publisher"
    CROSSREF = "crossref"
    OPENALEX = "openalex"
    REPOSITORY = "repository"
    AUTHOR_SITE = "author_site"
    OTHER = "other"


# ---------------------------------------------------------------------------
# ACCESS EVIDENCE RECORD
# ---------------------------------------------------------------------------
class AccessEvidenceRecord(
    BaseModel
):
    evidence_id: str

    access_id: str

    candidate_id: str

    evidence_type: AccessEvidenceType

    source: AccessEvidenceSource

    source_name: str | None = None

    source_url: str | None = None

    value: str | None = None

    basis: str | None = None

    observed_date: date | None = None

    notes: str | None = None

    @field_validator(
        "evidence_id",
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
        "source_name",
        "source_url",
        "value",
        "basis",
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

