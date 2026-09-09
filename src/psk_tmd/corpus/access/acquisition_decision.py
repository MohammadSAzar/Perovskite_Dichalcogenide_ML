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
from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyResolution,
    CombinedPolicyStatus,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
    TDMStatus,
)


# ---------------------------------------------------------------------------
# ACQUISITION DECISION
# ---------------------------------------------------------------------------
class AcquisitionDecision(
    str,
    Enum,
):
    AUTO_ACQUIRE = "auto_acquire"

    MANUAL_REVIEW = "manual_review"

    METADATA_ONLY = "metadata_only"


# ---------------------------------------------------------------------------
# ACQUISITION DECISION RESULT
# ---------------------------------------------------------------------------
class AcquisitionDecisionResult(
    BaseModel
):
    access_id: str

    candidate_id: str

    decision: AcquisitionDecision

    route: AcquisitionRoute

    source_url: str | None = None

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
                "Required acquisition decision "
                "field must not be empty."
            )

        return normalized

    @field_validator(
        "source_url",
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
# RESOLVE ACQUISITION DECISION
# ---------------------------------------------------------------------------
def resolve_acquisition_decision(
    *,
    access_id: str,
    candidate_id: str,
    route: AcquisitionRoute,
    source_url: str | None,
    url_verified: bool,
    appears_pdf: bool,
    policy: CombinedPolicyResolution,
) -> AcquisitionDecisionResult:
    if (
        policy.tdm_status
        == TDMStatus.NOT_PERMITTED
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.METADATA_ONLY
            ),
            route=(
                AcquisitionRoute.NONE
            ),
            source_url=None,
            reason=(
                "TDM is explicitly not permitted "
                "under the combined policy "
                "resolution."
            ),
        )

    if (
        route
        == AcquisitionRoute.NONE
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "No executable acquisition route "
                "has been resolved."
            ),
        )

    if (
        policy.automated_access_status
        == CombinedPolicyStatus.NOT_PERMITTED
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "Automated access is explicitly "
                "not permitted for the current "
                "provider route."
            ),
        )

    if (
        policy.tdm_status
        != TDMStatus.PERMITTED
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "TDM permission is not yet "
                "resolved as permitted."
            ),
        )

    if (
        policy.automated_access_status
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "Automated access permission is "
                "not sufficiently resolved."
            ),
        )

    if (
        policy.local_copy_status
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "Permission to retain a local "
                "working copy is not sufficiently "
                "resolved."
            ),
        )

    if not url_verified:
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "The proposed acquisition URL "
                "has not been successfully "
                "verified."
            ),
        )

    if not appears_pdf:
        return AcquisitionDecisionResult(
            access_id=access_id,
            candidate_id=candidate_id,
            decision=(
                AcquisitionDecision.MANUAL_REVIEW
            ),
            route=route,
            source_url=source_url,
            reason=(
                "The verified URL did not return "
                "confirmed PDF content."
            ),
        )

    return AcquisitionDecisionResult(
        access_id=access_id,
        candidate_id=candidate_id,
        decision=(
            AcquisitionDecision.AUTO_ACQUIRE
        ),
        route=route,
        source_url=source_url,
        reason=(
            "TDM is permitted, automated access "
            "is permitted or conditional, local "
            "copying is permitted or conditional, "
            "and the acquisition URL is verified "
            "as PDF content."
        ),
    )

