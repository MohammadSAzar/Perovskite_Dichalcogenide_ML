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
from psk_tmd.corpus.access.models import (
    TDMStatus,
)


# ---------------------------------------------------------------------------
# POLICY BASIS TYPE
# ---------------------------------------------------------------------------
class PolicyBasisType(
    str,
    Enum,
):
    LICENSE_TERMS = "license_terms"

    PUBLISHER_TDM_TERMS = (
        "publisher_tdm_terms"
    )

    REPOSITORY_TERMS = (
        "repository_terms"
    )

    CONTRACT_TERMS = (
        "contract_terms"
    )

    OTHER = "other"

    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# AI USE STATUS
# ---------------------------------------------------------------------------
class AIUseStatus(
    str,
    Enum,
):
    PERMITTED = "permitted"

    NOT_PERMITTED = "not_permitted"

    UNCLEAR = "unclear"

    NOT_EVALUATED = "not_evaluated"


# ---------------------------------------------------------------------------
# TDM POLICY ASSESSMENT
# ---------------------------------------------------------------------------
class TDMPolicyAssessment(
    BaseModel
):
    policy_id: str

    access_id: str

    candidate_id: str

    tdm_status: TDMStatus

    ai_use_status: AIUseStatus = (
        AIUseStatus.NOT_EVALUATED
    )

    basis_type: PolicyBasisType

    license_name: str | None = None

    policy_url: str | None = None

    jurisdiction: str | None = None

    basis_text: str | None = None

    automated_access_permitted: (
        bool
        | None
    ) = None

    local_copy_permitted: (
        bool
        | None
    ) = None

    redistribution_permitted: (
        bool
        | None
    ) = None

    notes: str | None = None

    @field_validator(
        "policy_id",
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
                "Required policy field "
                "must not be empty."
            )

        return normalized

    @field_validator(
        "license_name",
        "policy_url",
        "jurisdiction",
        "basis_text",
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

