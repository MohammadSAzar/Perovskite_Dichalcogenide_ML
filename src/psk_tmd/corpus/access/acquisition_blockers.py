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
# ACQUISITION BLOCKER TYPE
# ---------------------------------------------------------------------------
class AcquisitionBlockerType(
    str,
    Enum,
):
    NO_ROUTE = "no_route"

    TDM_NOT_PERMITTED = (
        "tdm_not_permitted"
    )

    TDM_UNRESOLVED = (
        "tdm_unresolved"
    )

    AUTOMATED_ACCESS_NOT_PERMITTED = (
        "automated_access_not_permitted"
    )

    AUTOMATED_ACCESS_UNRESOLVED = (
        "automated_access_unresolved"
    )

    LOCAL_COPY_NOT_PERMITTED = (
        "local_copy_not_permitted"
    )

    LOCAL_COPY_UNRESOLVED = (
        "local_copy_unresolved"
    )

    URL_NOT_VERIFIED = (
        "url_not_verified"
    )

    PDF_NOT_VERIFIED = (
        "pdf_not_verified"
    )


# ---------------------------------------------------------------------------
# ACQUISITION BLOCKER
# ---------------------------------------------------------------------------
class AcquisitionBlocker(
    BaseModel
):
    blocker_type: AcquisitionBlockerType

    reason: str

    @field_validator(
        "reason",
    )
    @classmethod
    def validate_reason(
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
                "Acquisition blocker reason "
                "must not be empty."
            )

        return normalized


# ---------------------------------------------------------------------------
# ACQUISITION BLOCKER ASSESSMENT
# ---------------------------------------------------------------------------
class AcquisitionBlockerAssessment(
    BaseModel
):
    access_id: str

    candidate_id: str

    blockers: list[
        AcquisitionBlocker
    ]

    is_blocked: bool

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
                "Required blocker assessment "
                "field must not be empty."
            )

        return normalized


# ---------------------------------------------------------------------------
# BUILD BLOCKER
# ---------------------------------------------------------------------------
def build_blocker(
    blocker_type: AcquisitionBlockerType,
    reason: str,
) -> AcquisitionBlocker:
    return AcquisitionBlocker(
        blocker_type=(
            blocker_type
        ),
        reason=(
            reason
        ),
    )


# ---------------------------------------------------------------------------
# ASSESS ACQUISITION BLOCKERS
# ---------------------------------------------------------------------------
def assess_acquisition_blockers(
    *,
    access_id: str,
    candidate_id: str,
    route: AcquisitionRoute,
    url_verified: bool,
    appears_pdf: bool,
    policy: CombinedPolicyResolution,
) -> AcquisitionBlockerAssessment:
    blockers = []

    if (
        route
        == AcquisitionRoute.NONE
    ):
        blockers.append(
            build_blocker(
                AcquisitionBlockerType.NO_ROUTE,
                (
                    "No executable acquisition "
                    "route has been resolved."
                ),
            )
        )

    if (
        policy.tdm_status
        == TDMStatus.NOT_PERMITTED
    ):
        blockers.append(
            build_blocker(
                AcquisitionBlockerType.TDM_NOT_PERMITTED,
                (
                    "TDM is explicitly not "
                    "permitted."
                ),
            )
        )

    elif (
        policy.tdm_status
        != TDMStatus.PERMITTED
    ):
        blockers.append(
            build_blocker(
                AcquisitionBlockerType.TDM_UNRESOLVED,
                (
                    "TDM permission is not "
                    "resolved as permitted."
                ),
            )
        )

    if (
        policy.automated_access_status
        == CombinedPolicyStatus.NOT_PERMITTED
    ):
        blockers.append(
            build_blocker(
                (
                    AcquisitionBlockerType
                    .AUTOMATED_ACCESS_NOT_PERMITTED
                ),
                (
                    "Automated access is "
                    "explicitly not permitted "
                    "for the current provider "
                    "route."
                ),
            )
        )

    elif (
        policy.automated_access_status
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        blockers.append(
            build_blocker(
                (
                    AcquisitionBlockerType
                    .AUTOMATED_ACCESS_UNRESOLVED
                ),
                (
                    "Automated access permission "
                    "is not sufficiently "
                    "resolved."
                ),
            )
        )

    if (
        policy.local_copy_status
        == CombinedPolicyStatus.NOT_PERMITTED
    ):
        blockers.append(
            build_blocker(
                (
                    AcquisitionBlockerType
                    .LOCAL_COPY_NOT_PERMITTED
                ),
                (
                    "Local-copy permission is "
                    "explicitly not permitted."
                ),
            )
        )

    elif (
        policy.local_copy_status
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        blockers.append(
            build_blocker(
                (
                    AcquisitionBlockerType
                    .LOCAL_COPY_UNRESOLVED
                ),
                (
                    "Local-copy permission is "
                    "not sufficiently resolved."
                ),
            )
        )

    if not url_verified:
        blockers.append(
            build_blocker(
                AcquisitionBlockerType.URL_NOT_VERIFIED,
                (
                    "The acquisition URL has "
                    "not been successfully "
                    "verified."
                ),
            )
        )

    if not appears_pdf:
        blockers.append(
            build_blocker(
                AcquisitionBlockerType.PDF_NOT_VERIFIED,
                (
                    "Confirmed PDF content has "
                    "not been verified."
                ),
            )
        )

    return AcquisitionBlockerAssessment(
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        blockers=(
            blockers
        ),
        is_blocked=(
            bool(
                blockers
            )
        ),
    )


