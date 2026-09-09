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
# POLICY PROVIDER TYPE
# ---------------------------------------------------------------------------
class PolicyProviderType(
    str,
    Enum,
):
    PUBLISHER = "publisher"

    REPOSITORY = "repository"

    OTHER = "other"


# ---------------------------------------------------------------------------
# POLICY SCOPE
# ---------------------------------------------------------------------------
class PolicyScope(
    str,
    Enum,
):
    TDM = "tdm"

    AUTOMATED_ACCESS = (
        "automated_access"
    )

    LOCAL_COPY = "local_copy"

    REDISTRIBUTION = (
        "redistribution"
    )

    AI_USE = "ai_use"


# ---------------------------------------------------------------------------
# POLICY DECISION
# ---------------------------------------------------------------------------
class PolicyDecision(
    str,
    Enum,
):
    PERMITTED = "permitted"

    NOT_PERMITTED = (
        "not_permitted"
    )

    CONDITIONAL = "conditional"

    UNCLEAR = "unclear"


# ---------------------------------------------------------------------------
# POLICY EVIDENCE RECORD
# ---------------------------------------------------------------------------
class PolicyEvidenceRecord(
    BaseModel
):
    evidence_id: str

    provider_key: str

    provider_name: str

    provider_type: PolicyProviderType

    scope: PolicyScope

    decision: PolicyDecision

    source_url: str

    observed_date: date

    basis_text: str

    conditions: str | None = None

    notes: str | None = None

    @field_validator(
        "evidence_id",
        "provider_key",
        "provider_name",
        "source_url",
        "basis_text",
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
                "Required policy evidence "
                "field must not be empty."
            )

        return normalized

    @field_validator(
        "conditions",
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

        return (
            normalized
            or None
        )

    @field_validator(
        "provider_key",
    )
    @classmethod
    def normalize_provider_key(
        cls,
        value: str,
    ) -> str:
        normalized = (
            value
            .strip()
            .lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "-",
                "_",
            )
        )

        if not normalized:
            raise ValueError(
                "provider_key "
                "must not be empty."
            )

        return normalized

