from psk_tmd.corpus.access.license import (
    NormalizedLicenseType,
    normalize_license,
)
from psk_tmd.corpus.access.license_policy import (
    build_license_basis_text,
    build_license_policy_assessment,
    resolve_license_tdm_status,
    resolve_local_copy_permission,
    resolve_redistribution_permission,
)
from psk_tmd.corpus.access.models import (
    TDMStatus,
)
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
    PolicyBasisType,
)


# ---------------------------------------------------------------------------
# CC BY PERMITS LICENSE-BASED TDM
# ---------------------------------------------------------------------------
def test_cc_by_permits_license_based_tdm():
    license_value = (
        normalize_license(
            "cc-by"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# CC0 PERMITS LICENSE-BASED TDM
# ---------------------------------------------------------------------------
def test_cc0_permits_license_based_tdm():
    license_value = (
        normalize_license(
            "CC0 1.0"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# PUBLIC DOMAIN PERMITS LICENSE-BASED TDM
# ---------------------------------------------------------------------------
def test_public_domain_permits_license_based_tdm():
    license_value = (
        normalize_license(
            "Public Domain"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# CC BY NC REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_cc_by_nc_requires_review():
    license_value = (
        normalize_license(
            "CC BY-NC 4.0"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# CC BY ND REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_cc_by_nd_requires_review():
    license_value = (
        normalize_license(
            "CC BY-ND 4.0"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# CC BY NC ND REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_cc_by_nc_nd_requires_review():
    license_value = (
        normalize_license(
            "cc-by-nc-nd"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# UNKNOWN LICENSE IS NOT EVALUATED
# ---------------------------------------------------------------------------
def test_unknown_license_is_not_evaluated():
    license_value = (
        normalize_license(
            None
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# OTHER LICENSE IS UNCLEAR
# ---------------------------------------------------------------------------
def test_other_license_is_unclear():
    license_value = (
        normalize_license(
            "Example Custom License"
        )
    )

    assert (
        resolve_license_tdm_status(
            license_value
        )
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# PERMISSIVE LICENSE ALLOWS LOCAL COPY
# ---------------------------------------------------------------------------
def test_permissive_license_allows_local_copy():
    license_value = (
        normalize_license(
            "CC BY 4.0"
        )
    )

    assert (
        resolve_local_copy_permission(
            license_value
        )
        is True
    )


# ---------------------------------------------------------------------------
# RESTRICTED LICENSE LOCAL COPY UNKNOWN
# ---------------------------------------------------------------------------
def test_restricted_license_local_copy_unknown():
    license_value = (
        normalize_license(
            "CC BY-NC-ND 4.0"
        )
    )

    assert (
        resolve_local_copy_permission(
            license_value
        )
        is None
    )


# ---------------------------------------------------------------------------
# CC BY REDISTRIBUTION PERMITTED
# ---------------------------------------------------------------------------
def test_cc_by_redistribution_permitted():
    license_value = (
        normalize_license(
            "CC BY 4.0"
        )
    )

    assert (
        resolve_redistribution_permission(
            license_value
        )
        is True
    )


# ---------------------------------------------------------------------------
# RESTRICTED REDISTRIBUTION UNKNOWN
# ---------------------------------------------------------------------------
def test_restricted_redistribution_unknown():
    license_value = (
        normalize_license(
            "CC BY-NC-ND 4.0"
        )
    )

    assert (
        resolve_redistribution_permission(
            license_value
        )
        is None
    )


# ---------------------------------------------------------------------------
# BUILD CC BY POLICY ASSESSMENT
# ---------------------------------------------------------------------------
def test_build_cc_by_policy_assessment():
    license_value = (
        normalize_license(
            "CC BY 4.0"
        )
    )

    assessment = (
        build_license_policy_assessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            license_value=(
                license_value
            ),
            policy_url=(
                "https://creativecommons.org/"
                "licenses/by/4.0/"
            ),
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.PERMITTED
    )

    assert (
        assessment.ai_use_status
        == AIUseStatus.NOT_EVALUATED
    )

    assert (
        assessment.basis_type
        == PolicyBasisType.LICENSE_TERMS
    )

    assert (
        assessment.license_name
        == "CC BY 4.0"
    )

    assert (
        assessment.automated_access_permitted
        is None
    )

    assert (
        assessment.local_copy_permitted
        is True
    )


# ---------------------------------------------------------------------------
# BUILD RESTRICTED POLICY ASSESSMENT
# ---------------------------------------------------------------------------
def test_build_restricted_policy_assessment():
    license_value = (
        normalize_license(
            "cc-by-nc-nd"
        )
    )

    assessment = (
        build_license_policy_assessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            license_value=(
                license_value
            ),
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.UNCLEAR
    )

    assert (
        assessment.local_copy_permitted
        is None
    )

    assert (
        assessment.redistribution_permitted
        is None
    )


# ---------------------------------------------------------------------------
# BASIS TEXT DESCRIBES RESTRICTION
# ---------------------------------------------------------------------------
def test_basis_text_describes_restriction():
    license_value = (
        normalize_license(
            "CC BY-NC-ND 4.0"
        )
    )

    basis_text = (
        build_license_basis_text(
            license_value
        )
    )

    assert (
        "non-commercial"
        in basis_text
    )

    assert (
        "no-derivatives"
        in basis_text
    )


# ---------------------------------------------------------------------------
# LICENSE TYPE IS PRESERVED
# ---------------------------------------------------------------------------
def test_license_type_is_preserved():
    license_value = (
        normalize_license(
            "CC BY-SA 4.0"
        )
    )

    assert (
        license_value.license_type
        == NormalizedLicenseType.CC_BY_SA
    )

