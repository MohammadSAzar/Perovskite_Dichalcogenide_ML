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
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
    TDMPolicyAssessment,
)
from psk_tmd.corpus.access.policy_evidence import (
    PolicyDecision,
    PolicyEvidenceRecord,
    PolicyScope,
)


# ---------------------------------------------------------------------------
# COMBINED POLICY STATUS
# ---------------------------------------------------------------------------
class CombinedPolicyStatus(
    str,
    Enum,
):
    PERMITTED = "permitted"

    NOT_PERMITTED = "not_permitted"

    CONDITIONAL = "conditional"

    UNCLEAR = "unclear"

    NOT_EVALUATED = "not_evaluated"


# ---------------------------------------------------------------------------
# COMBINED POLICY RESOLUTION
# ---------------------------------------------------------------------------
class CombinedPolicyResolution(
    BaseModel
):
    access_id: str

    candidate_id: str

    provider_key: str | None = None

    tdm_status: TDMStatus

    automated_access_status: (
        CombinedPolicyStatus
    )

    local_copy_status: (
        CombinedPolicyStatus
    )

    redistribution_status: (
        CombinedPolicyStatus
    )

    ai_use_status: AIUseStatus

    license_policy_id: str | None = None

    provider_evidence_ids: list[
        str
    ] = []

    conditions: list[
        str
    ] = []

    reason: str

    @field_validator(
        "access_id",
        "candidate_id",
        "reason",
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
                "Required combined policy "
                "field must not be empty."
            )

        return normalized

    @field_validator(
        "provider_key",
        "license_policy_id",
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


# ---------------------------------------------------------------------------
# INDEX PROVIDER EVIDENCE BY SCOPE
# ---------------------------------------------------------------------------
def index_provider_evidence_by_scope(
    evidence_records: list[
        PolicyEvidenceRecord
    ],
) -> dict[
    PolicyScope,
    PolicyEvidenceRecord,
]:
    index = {}

    for evidence in evidence_records:
        scope = (
            evidence.scope
        )

        if scope in index:
            raise ValueError(
                "Multiple provider policy "
                "evidence records exist for "
                f"scope={scope.value}. "
                "Conflicting or duplicate "
                "provider evidence must be "
                "reviewed explicitly."
            )

        index[
            scope
        ] = evidence

    return index


# ---------------------------------------------------------------------------
# RESOLVE TDM STATUS
# ---------------------------------------------------------------------------
def resolve_combined_tdm_status(
    *,
    license_status: TDMStatus,
    provider_evidence: (
        PolicyEvidenceRecord
        | None
    ),
) -> TDMStatus:
    if (
        provider_evidence is not None
        and provider_evidence.decision
        == PolicyDecision.NOT_PERMITTED
    ):
        return (
            TDMStatus.NOT_PERMITTED
        )

    if (
        license_status
        == TDMStatus.NOT_PERMITTED
    ):
        return (
            TDMStatus.NOT_PERMITTED
        )

    if (
        license_status
        == TDMStatus.PERMITTED
    ):
        return (
            TDMStatus.PERMITTED
        )

    if (
        license_status
        == TDMStatus.UNCLEAR
    ):
        if (
            provider_evidence is not None
            and provider_evidence.decision
            == PolicyDecision.PERMITTED
        ):
            return (
                TDMStatus.PERMITTED
            )

        return (
            TDMStatus.UNCLEAR
        )

    if (
        provider_evidence is None
    ):
        return (
            TDMStatus.NOT_EVALUATED
        )

    if (
        provider_evidence.decision
        == PolicyDecision.PERMITTED
    ):
        return (
            TDMStatus.PERMITTED
        )

    if (
        provider_evidence.decision
        in {
            PolicyDecision.CONDITIONAL,
            PolicyDecision.UNCLEAR,
        }
    ):
        return (
            TDMStatus.UNCLEAR
        )

    return (
        TDMStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# RESOLVE BOOLEAN LICENSE PERMISSION
# ---------------------------------------------------------------------------
def resolve_boolean_permission(
    *,
    license_permission: (
        bool
        | None
    ),
    provider_evidence: (
        PolicyEvidenceRecord
        | None
    ),
) -> CombinedPolicyStatus:
    if (
        provider_evidence is not None
        and provider_evidence.decision
        == PolicyDecision.NOT_PERMITTED
    ):
        return (
            CombinedPolicyStatus.NOT_PERMITTED
        )

    if (
        license_permission is False
    ):
        return (
            CombinedPolicyStatus.NOT_PERMITTED
        )

    if provider_evidence is not None:
        if (
            provider_evidence.decision
            == PolicyDecision.CONDITIONAL
        ):
            return (
                CombinedPolicyStatus.CONDITIONAL
            )

        if (
            provider_evidence.decision
            == PolicyDecision.PERMITTED
        ):
            return (
                CombinedPolicyStatus.PERMITTED
            )

        if (
            provider_evidence.decision
            == PolicyDecision.UNCLEAR
        ):
            if (
                license_permission
                is True
            ):
                return (
                    CombinedPolicyStatus.PERMITTED
                )

            return (
                CombinedPolicyStatus.UNCLEAR
            )

    if (
        license_permission is True
    ):
        return (
            CombinedPolicyStatus.PERMITTED
        )

    return (
        CombinedPolicyStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# RESOLVE AUTOMATED ACCESS STATUS
# ---------------------------------------------------------------------------
def resolve_automated_access_status(
    provider_evidence: (
        PolicyEvidenceRecord
        | None
    ),
) -> CombinedPolicyStatus:
    if provider_evidence is None:
        return (
            CombinedPolicyStatus.NOT_EVALUATED
        )

    decision_mapping = {
        PolicyDecision.PERMITTED: (
            CombinedPolicyStatus.PERMITTED
        ),
        PolicyDecision.NOT_PERMITTED: (
            CombinedPolicyStatus.NOT_PERMITTED
        ),
        PolicyDecision.CONDITIONAL: (
            CombinedPolicyStatus.CONDITIONAL
        ),
        PolicyDecision.UNCLEAR: (
            CombinedPolicyStatus.UNCLEAR
        ),
    }

    return (
        decision_mapping[
            provider_evidence.decision
        ]
    )


# ---------------------------------------------------------------------------
# COLLECT PROVIDER CONDITIONS
# ---------------------------------------------------------------------------
def collect_provider_conditions(
    evidence_records: list[
        PolicyEvidenceRecord
    ],
) -> list[
    str
]:
    conditions = []

    for evidence in evidence_records:
        if evidence.conditions is None:
            continue

        if (
            evidence.conditions
            not in conditions
        ):
            conditions.append(
                evidence.conditions
            )

    return conditions


# ---------------------------------------------------------------------------
# BUILD COMBINED POLICY RESOLUTION
# ---------------------------------------------------------------------------
def build_combined_policy_resolution(
    *,
    access_id: str,
    candidate_id: str,
    provider_key: str | None,
    license_assessment: (
        TDMPolicyAssessment
        | None
    ),
    provider_evidence_records: list[
        PolicyEvidenceRecord
    ],
) -> CombinedPolicyResolution:
    evidence_by_scope = (
        index_provider_evidence_by_scope(
            provider_evidence_records
        )
    )

    tdm_evidence = (
        evidence_by_scope.get(
            PolicyScope.TDM
        )
    )

    automated_evidence = (
        evidence_by_scope.get(
            PolicyScope.AUTOMATED_ACCESS
        )
    )

    local_copy_evidence = (
        evidence_by_scope.get(
            PolicyScope.LOCAL_COPY
        )
    )

    redistribution_evidence = (
        evidence_by_scope.get(
            PolicyScope.REDISTRIBUTION
        )
    )

    ai_evidence = (
        evidence_by_scope.get(
            PolicyScope.AI_USE
        )
    )

    if license_assessment is None:
        license_tdm_status = (
            TDMStatus.NOT_EVALUATED
        )

        license_local_copy = None

        license_redistribution = None

        license_ai_status = (
            AIUseStatus.NOT_EVALUATED
        )

        license_policy_id = None

    else:
        license_tdm_status = (
            license_assessment.tdm_status
        )

        license_local_copy = (
            license_assessment
            .local_copy_permitted
        )

        license_redistribution = (
            license_assessment
            .redistribution_permitted
        )

        license_ai_status = (
            license_assessment
            .ai_use_status
        )

        license_policy_id = (
            license_assessment.policy_id
        )

    tdm_status = (
        resolve_combined_tdm_status(
            license_status=(
                license_tdm_status
            ),
            provider_evidence=(
                tdm_evidence
            ),
        )
    )

    automated_access_status = (
        resolve_automated_access_status(
            automated_evidence
        )
    )

    local_copy_status = (
        resolve_boolean_permission(
            license_permission=(
                license_local_copy
            ),
            provider_evidence=(
                local_copy_evidence
            ),
        )
    )

    redistribution_status = (
        resolve_boolean_permission(
            license_permission=(
                license_redistribution
            ),
            provider_evidence=(
                redistribution_evidence
            ),
        )
    )

    ai_use_status = (
        license_ai_status
    )

    if ai_evidence is not None:
        if (
            ai_evidence.decision
            == PolicyDecision.PERMITTED
        ):
            ai_use_status = (
                AIUseStatus.PERMITTED
            )

        elif (
            ai_evidence.decision
            == PolicyDecision.NOT_PERMITTED
        ):
            ai_use_status = (
                AIUseStatus.NOT_PERMITTED
            )

        else:
            ai_use_status = (
                AIUseStatus.UNCLEAR
            )

    provider_evidence_ids = [
        evidence.evidence_id
        for evidence
        in provider_evidence_records
    ]

    conditions = (
        collect_provider_conditions(
            provider_evidence_records
        )
    )

    return CombinedPolicyResolution(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        provider_key=(
            provider_key
        ),
        tdm_status=(
            tdm_status
        ),
        automated_access_status=(
            automated_access_status
        ),
        local_copy_status=(
            local_copy_status
        ),
        redistribution_status=(
            redistribution_status
        ),
        ai_use_status=(
            ai_use_status
        ),
        license_policy_id=(
            license_policy_id
        ),
        provider_evidence_ids=(
            provider_evidence_ids
        ),
        conditions=(
            conditions
        ),
        reason=(
            "Combined policy resolution was "
            "derived from article-level "
            "license assessment and "
            "provider-level policy evidence. "
            "TDM, automated access, local "
            "copying, redistribution, and "
            "AI use were resolved as "
            "separate dimensions."
        ),
    )

