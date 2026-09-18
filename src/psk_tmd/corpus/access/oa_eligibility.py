from enum import (
    Enum,
)

from pydantic import (
    BaseModel,
)

from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyStatus,
)
from psk_tmd.corpus.access.location import (
    AccessLocationType,
)


# ---------------------------------------------------------------------------
# OA ACQUISITION MODE
# ---------------------------------------------------------------------------
class OAAcquisitionMode(
    str,
    Enum,
):
    AUTOMATED = "automated"

    MANUAL_REVIEW = "manual_review"

    METADATA_ONLY = "metadata_only"


# ---------------------------------------------------------------------------
# OA PREFERRED SOURCE
# ---------------------------------------------------------------------------
class OAPreferredSource(
    str,
    Enum,
):
    REPOSITORY = "repository"

    PUBLISHER = "publisher"

    OTHER = "other"

    NONE = "none"


# ---------------------------------------------------------------------------
# OA ELIGIBILITY RESOLUTION
# ---------------------------------------------------------------------------
class OAEligibilityResolution(
    BaseModel
):
    access_id: str

    candidate_id: str

    eligible_for_oa_acquisition: bool

    acquisition_mode: (
        OAAcquisitionMode
    )

    preferred_source: (
        OAPreferredSource
    )

    source_url: str | None = None

    pdf_verified: bool

    tdm_status: (
        CombinedPolicyStatus
    )

    automated_access_status: (
        CombinedPolicyStatus
    )

    local_copy_status: (
        CombinedPolicyStatus
    )

    reason: str


# ---------------------------------------------------------------------------
# RESOLVE PREFERRED SOURCE
# ---------------------------------------------------------------------------
def resolve_preferred_source(
    location_type: (
        AccessLocationType
        | str
        | None
    ),
) -> OAPreferredSource:
    if (
        location_type
        == AccessLocationType.REPOSITORY
        or location_type
        == "repository"
    ):
        return (
            OAPreferredSource.REPOSITORY
        )

    if (
        location_type
        == AccessLocationType.PUBLISHER
        or location_type
        == "publisher"
    ):
        return (
            OAPreferredSource.PUBLISHER
        )

    if (
        location_type
        in {
            AccessLocationType.OTHER,
            "other",
        }
    ):
        return (
            OAPreferredSource.OTHER
        )

    return (
        OAPreferredSource.NONE
    )


# ---------------------------------------------------------------------------
# NORMALIZE POLICY STATUS
# ---------------------------------------------------------------------------
def normalize_policy_status(
    value: (
        CombinedPolicyStatus
        | str
    ),
) -> CombinedPolicyStatus:
    if isinstance(
        value,
        CombinedPolicyStatus,
    ):
        return value

    return (
        CombinedPolicyStatus(
            value
        )
    )


# ---------------------------------------------------------------------------
# RESOLVE OA ELIGIBILITY
# ---------------------------------------------------------------------------
def resolve_oa_eligibility(
    *,
    access_id: str,
    candidate_id: str,
    location_type: (
        AccessLocationType
        | str
        | None
    ),
    source_url: str | None,
    url_verified: bool,
    appears_pdf: bool,
    tdm_status: (
        CombinedPolicyStatus
        | str
    ),
    automated_access_status: (
        CombinedPolicyStatus
        | str
    ),
    local_copy_status: (
        CombinedPolicyStatus
        | str
    ),
) -> OAEligibilityResolution:
    tdm = (
        normalize_policy_status(
            tdm_status
        )
    )

    automated_access = (
        normalize_policy_status(
            automated_access_status
        )
    )

    local_copy = (
        normalize_policy_status(
            local_copy_status
        )
    )

    preferred_source = (
        resolve_preferred_source(
            location_type
        )
    )

    pdf_verified = (
        url_verified
        and appears_pdf
    )

    if (
        tdm
        == CombinedPolicyStatus.NOT_PERMITTED
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=False,
            acquisition_mode=(
                OAAcquisitionMode.METADATA_ONLY
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=(
                pdf_verified
            ),
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "TDM is explicitly "
                "not permitted."
            ),
        )

    if (
        local_copy
        == CombinedPolicyStatus.NOT_PERMITTED
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=False,
            acquisition_mode=(
                OAAcquisitionMode.METADATA_ONLY
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=(
                pdf_verified
            ),
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "Local full-text copy is "
                "explicitly not permitted."
            ),
        )

    if (
        preferred_source
        == OAPreferredSource.NONE
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=False,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=(
                pdf_verified
            ),
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "No repository or publisher "
                "OA source is currently "
                "resolved."
            ),
        )

    if not source_url:
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=False,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=None,
            pdf_verified=(
                pdf_verified
            ),
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "OA source type is known, "
                "but no stable source URL "
                "is available."
            ),
        )

    if (
        not pdf_verified
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=True,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=False,
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "An OA source exists, but "
                "machine-readable PDF access "
                "has not been verified."
            ),
        )

    if (
        tdm
        != CombinedPolicyStatus.PERMITTED
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=True,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=True,
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "PDF access is verified, but "
                "TDM permission is not yet "
                "resolved as permitted."
            ),
        )

    if (
        automated_access
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=True,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=True,
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "TDM is permitted, but "
                "automated access permission "
                "is unresolved."
            ),
        )

    if (
        local_copy
        not in {
            CombinedPolicyStatus.PERMITTED,
            CombinedPolicyStatus.CONDITIONAL,
        }
    ):
        return OAEligibilityResolution(
            access_id=access_id,
            candidate_id=candidate_id,
            eligible_for_oa_acquisition=True,
            acquisition_mode=(
                OAAcquisitionMode.MANUAL_REVIEW
            ),
            preferred_source=(
                preferred_source
            ),
            source_url=(
                source_url
            ),
            pdf_verified=True,
            tdm_status=(
                tdm
            ),
            automated_access_status=(
                automated_access
            ),
            local_copy_status=(
                local_copy
            ),
            reason=(
                "TDM is permitted, but "
                "local-copy permission is "
                "unresolved."
            ),
        )

    return OAEligibilityResolution(
        access_id=access_id,
        candidate_id=candidate_id,
        eligible_for_oa_acquisition=True,
        acquisition_mode=(
            OAAcquisitionMode.AUTOMATED
        ),
        preferred_source=(
            preferred_source
        ),
        source_url=(
            source_url
        ),
        pdf_verified=True,
        tdm_status=(
            tdm
        ),
        automated_access_status=(
            automated_access
        ),
        local_copy_status=(
            local_copy
        ),
        reason=(
            "OA PDF access is verified and "
            "the current policy evidence "
            "supports automated acquisition "
            "for local research use."
        ),
    )


