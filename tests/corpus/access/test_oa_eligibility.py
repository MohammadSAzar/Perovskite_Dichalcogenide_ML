from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyStatus,
)
from psk_tmd.corpus.access.location import (
    AccessLocationType,
)
from psk_tmd.corpus.access.oa_eligibility import (
    OAAcquisitionMode,
    OAPreferredSource,
    resolve_oa_eligibility,
    resolve_preferred_source,
)


# ---------------------------------------------------------------------------
# REPOSITORY IS PREFERRED SOURCE
# ---------------------------------------------------------------------------
def test_repository_is_preferred_source():
    assert (
        resolve_preferred_source(
            AccessLocationType.REPOSITORY
        )
        == OAPreferredSource.REPOSITORY
    )


# ---------------------------------------------------------------------------
# PUBLISHER IS PREFERRED SOURCE
# ---------------------------------------------------------------------------
def test_publisher_is_preferred_source():
    assert (
        resolve_preferred_source(
            AccessLocationType.PUBLISHER
        )
        == OAPreferredSource.PUBLISHER
    )


# ---------------------------------------------------------------------------
# PERMITTED VERIFIED PDF IS AUTOMATED
# ---------------------------------------------------------------------------
def test_permitted_verified_pdf_is_automated():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-001",
            candidate_id="CND-TEST-001",
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            tdm_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            automated_access_status=(
                CombinedPolicyStatus.CONDITIONAL
            ),
            local_copy_status=(
                CombinedPolicyStatus.CONDITIONAL
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is True
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.AUTOMATED
    )

    assert (
        result.pdf_verified
        is True
    )


# ---------------------------------------------------------------------------
# UNRESOLVED TDM REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unresolved_tdm_requires_review():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-002",
            candidate_id="CND-TEST-002",
            location_type=(
                AccessLocationType.REPOSITORY
            ),
            source_url=(
                "https://arxiv.org/pdf/example"
            ),
            url_verified=True,
            appears_pdf=True,
            tdm_status=(
                CombinedPolicyStatus.NOT_EVALUATED
            ),
            automated_access_status=(
                CombinedPolicyStatus.UNCLEAR
            ),
            local_copy_status=(
                CombinedPolicyStatus.NOT_EVALUATED
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is True
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.MANUAL_REVIEW
    )


# ---------------------------------------------------------------------------
# UNVERIFIED PDF REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unverified_pdf_requires_review():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-003",
            candidate_id="CND-TEST-003",
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=False,
            appears_pdf=False,
            tdm_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            automated_access_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            local_copy_status=(
                CombinedPolicyStatus.PERMITTED
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is True
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.MANUAL_REVIEW
    )

    assert (
        result.pdf_verified
        is False
    )


# ---------------------------------------------------------------------------
# NO RESOLVED SOURCE REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_no_resolved_source_requires_review():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-004",
            candidate_id="CND-TEST-004",
            location_type=(
                AccessLocationType.DOI
            ),
            source_url=(
                "https://doi.org/example"
            ),
            url_verified=True,
            appears_pdf=False,
            tdm_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            automated_access_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            local_copy_status=(
                CombinedPolicyStatus.PERMITTED
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is False
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.MANUAL_REVIEW
    )

    assert (
        result.preferred_source
        == OAPreferredSource.NONE
    )


# ---------------------------------------------------------------------------
# TDM NOT PERMITTED IS METADATA ONLY
# ---------------------------------------------------------------------------
def test_tdm_not_permitted_is_metadata_only():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-005",
            candidate_id="CND-TEST-005",
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            tdm_status=(
                CombinedPolicyStatus.NOT_PERMITTED
            ),
            automated_access_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            local_copy_status=(
                CombinedPolicyStatus.PERMITTED
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is False
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.METADATA_ONLY
    )


# ---------------------------------------------------------------------------
# LOCAL COPY NOT PERMITTED IS METADATA ONLY
# ---------------------------------------------------------------------------
def test_local_copy_not_permitted_is_metadata_only():
    result = (
        resolve_oa_eligibility(
            access_id="ACC-TEST-006",
            candidate_id="CND-TEST-006",
            location_type=(
                AccessLocationType.PUBLISHER
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            tdm_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            automated_access_status=(
                CombinedPolicyStatus.PERMITTED
            ),
            local_copy_status=(
                CombinedPolicyStatus.NOT_PERMITTED
            ),
        )
    )

    assert (
        result.eligible_for_oa_acquisition
        is False
    )

    assert (
        result.acquisition_mode
        == OAAcquisitionMode.METADATA_ONLY
    )

