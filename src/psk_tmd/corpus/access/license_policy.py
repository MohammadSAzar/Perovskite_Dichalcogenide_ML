from psk_tmd.corpus.access.license import (
    NormalizedLicense,
    NormalizedLicenseType,
)
from psk_tmd.corpus.access.models import (
    TDMStatus,
)
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
    PolicyBasisType,
    TDMPolicyAssessment,
)


# ---------------------------------------------------------------------------
# PERMISSIVE LICENSE TYPES
# ---------------------------------------------------------------------------
PERMISSIVE_LICENSE_TYPES = {
    NormalizedLicenseType.CC0,
    NormalizedLicenseType.CC_BY,
    NormalizedLicenseType.CC_BY_SA,
    NormalizedLicenseType.PUBLIC_DOMAIN,
}


# ---------------------------------------------------------------------------
# RESTRICTED LICENSE TYPES
# ---------------------------------------------------------------------------
RESTRICTED_LICENSE_TYPES = {
    NormalizedLicenseType.CC_BY_ND,
    NormalizedLicenseType.CC_BY_NC,
    NormalizedLicenseType.CC_BY_NC_SA,
    NormalizedLicenseType.CC_BY_NC_ND,
}


# ---------------------------------------------------------------------------
# BUILD LICENSE BASIS TEXT
# ---------------------------------------------------------------------------
def build_license_basis_text(
    license_value: NormalizedLicense,
) -> str:
    license_name = (
        license_value.normalized_name
        or license_value.raw_value
        or "unknown"
    )

    license_type = (
        license_value.license_type
    )

    if (
        license_type
        == NormalizedLicenseType.CC0
    ):
        return (
            f"{license_name} is a highly "
            "permissive public-domain-style "
            "dedication. The license provides "
            "a strong basis for research reuse, "
            "but automated access to the hosting "
            "service must still be evaluated "
            "separately."
        )

    if (
        license_type
        == NormalizedLicenseType.PUBLIC_DOMAIN
    ):
        return (
            "The work is reported as public "
            "domain. This provides a strong "
            "reuse basis, but automated access "
            "to the hosting service must still "
            "be evaluated separately."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY
    ):
        return (
            f"{license_name} permits broad "
            "reuse subject to attribution. "
            "This provides a positive "
            "license-based signal for research "
            "TDM, while automated retrieval "
            "terms remain separate."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY_SA
    ):
        return (
            f"{license_name} permits reuse "
            "subject to attribution and "
            "share-alike obligations. This "
            "provides a positive license-based "
            "signal for research TDM, while "
            "automated retrieval terms remain "
            "separate."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY_NC
    ):
        return (
            f"{license_name} includes a "
            "non-commercial restriction. "
            "Whether the intended TDM use "
            "falls within that restriction "
            "requires contextual review."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY_ND
    ):
        return (
            f"{license_name} includes a "
            "no-derivatives restriction. "
            "The effect of that restriction "
            "on the intended TDM workflow "
            "requires policy review."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY_NC_SA
    ):
        return (
            f"{license_name} includes "
            "non-commercial and share-alike "
            "conditions. The intended TDM "
            "workflow requires contextual "
            "policy review."
        )

    if (
        license_type
        == NormalizedLicenseType.CC_BY_NC_ND
    ):
        return (
            f"{license_name} combines "
            "non-commercial and no-derivatives "
            "restrictions. The intended TDM "
            "workflow therefore requires "
            "policy review."
        )

    if (
        license_type
        == NormalizedLicenseType.OTHER
    ):
        return (
            "A license value is available, "
            "but it is not recognized by the "
            "current normalization rules. "
            "Manual policy review is required."
        )

    return (
        "No usable license information is "
        "available, so no license-based TDM "
        "conclusion can be made."
    )


# ---------------------------------------------------------------------------
# RESOLVE LICENSE TDM STATUS
# ---------------------------------------------------------------------------
def resolve_license_tdm_status(
    license_value: NormalizedLicense,
) -> TDMStatus:
    if (
        license_value.license_type
        in PERMISSIVE_LICENSE_TYPES
    ):
        return (
            TDMStatus.PERMITTED
        )

    if (
        license_value.license_type
        in RESTRICTED_LICENSE_TYPES
    ):
        return (
            TDMStatus.UNCLEAR
        )

    if (
        license_value.license_type
        == NormalizedLicenseType.OTHER
    ):
        return (
            TDMStatus.UNCLEAR
        )

    return (
        TDMStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# RESOLVE LOCAL COPY PERMISSION
# ---------------------------------------------------------------------------
def resolve_local_copy_permission(
    license_value: NormalizedLicense,
) -> bool | None:
    if (
        license_value.license_type
        in PERMISSIVE_LICENSE_TYPES
    ):
        return True

    return None


# ---------------------------------------------------------------------------
# RESOLVE REDISTRIBUTION PERMISSION
# ---------------------------------------------------------------------------
def resolve_redistribution_permission(
    license_value: NormalizedLicense,
) -> bool | None:
    if (
        license_value.license_type
        in {
            NormalizedLicenseType.CC0,
            NormalizedLicenseType.PUBLIC_DOMAIN,
            NormalizedLicenseType.CC_BY,
            NormalizedLicenseType.CC_BY_SA,
        }
    ):
        return True

    return None


# ---------------------------------------------------------------------------
# BUILD LICENSE POLICY ASSESSMENT
# ---------------------------------------------------------------------------
def build_license_policy_assessment(
    *,
    policy_id: str,
    access_id: str,
    candidate_id: str,
    license_value: NormalizedLicense,
    policy_url: str | None = None,
) -> TDMPolicyAssessment:
    tdm_status = (
        resolve_license_tdm_status(
            license_value
        )
    )

    return TDMPolicyAssessment(
        policy_id=(
            policy_id
        ),
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        tdm_status=(
            tdm_status
        ),
        ai_use_status=(
            AIUseStatus.NOT_EVALUATED
        ),
        basis_type=(
            PolicyBasisType.LICENSE_TERMS
        ),
        license_name=(
            license_value.normalized_name
            or license_value.raw_value
        ),
        policy_url=(
            policy_url
        ),
        basis_text=(
            build_license_basis_text(
                license_value
            )
        ),
        automated_access_permitted=None,
        local_copy_permitted=(
            resolve_local_copy_permission(
                license_value
            )
        ),
        redistribution_permitted=(
            resolve_redistribution_permission(
                license_value
            )
        ),
        notes=(
            "This assessment is based only "
            "on license metadata. Publisher "
            "or repository automated-access "
            "terms and AI-use permissions "
            "must be evaluated separately."
        ),
    )


