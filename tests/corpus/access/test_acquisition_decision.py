from psk_tmd.corpus.access.acquisition_decision import (
    AcquisitionDecision,
    resolve_acquisition_decision,
)
from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyResolution,
    CombinedPolicyStatus,
)
from psk_tmd.corpus.access.models import (
    AcquisitionRoute,
    TDMStatus,
)
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
)


# ---------------------------------------------------------------------------
# MAKE POLICY
# ---------------------------------------------------------------------------
def make_policy(
    *,
    tdm_status: TDMStatus = (
        TDMStatus.PERMITTED
    ),
    automated_access_status: (
        CombinedPolicyStatus
    ) = (
        CombinedPolicyStatus.PERMITTED
    ),
    local_copy_status: (
        CombinedPolicyStatus
    ) = (
        CombinedPolicyStatus.PERMITTED
    ),
) -> CombinedPolicyResolution:
    return CombinedPolicyResolution(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        provider_key="example",
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
            CombinedPolicyStatus.NOT_EVALUATED
        ),
        ai_use_status=(
            AIUseStatus.NOT_EVALUATED
        ),
        reason="Test policy.",
    )


# ---------------------------------------------------------------------------
# VERIFIED PDF CAN AUTO ACQUIRE
# ---------------------------------------------------------------------------
def test_verified_pdf_can_auto_acquire():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy()
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.AUTO_ACQUIRE
    )


# ---------------------------------------------------------------------------
# CONDITIONAL AUTOMATED ACCESS CAN AUTO ACQUIRE
# ---------------------------------------------------------------------------
def test_conditional_automated_access_can_auto_acquire():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    automated_access_status=(
                        CombinedPolicyStatus.CONDITIONAL
                    ),
                    local_copy_status=(
                        CombinedPolicyStatus.CONDITIONAL
                    ),
                )
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.AUTO_ACQUIRE
    )


# ---------------------------------------------------------------------------
# UNCLEAR TDM REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unclear_tdm_requires_review():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    tdm_status=(
                        TDMStatus.UNCLEAR
                    )
                )
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.MANUAL_REVIEW
    )


# ---------------------------------------------------------------------------
# NOT PERMITTED TDM BECOMES METADATA ONLY
# ---------------------------------------------------------------------------
def test_not_permitted_tdm_becomes_metadata_only():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    tdm_status=(
                        TDMStatus.NOT_PERMITTED
                    )
                )
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.METADATA_ONLY
    )


# ---------------------------------------------------------------------------
# UNCLEAR AUTOMATED ACCESS REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unclear_automated_access_requires_review():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    automated_access_status=(
                        CombinedPolicyStatus.UNCLEAR
                    )
                )
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.MANUAL_REVIEW
    )


# ---------------------------------------------------------------------------
# UNVERIFIED URL REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unverified_url_requires_review():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article.pdf"
            ),
            url_verified=False,
            appears_pdf=False,
            policy=(
                make_policy()
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.MANUAL_REVIEW
    )


# ---------------------------------------------------------------------------
# VERIFIED HTML REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_verified_html_requires_review():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            source_url=(
                "https://example.org/article"
            ),
            url_verified=True,
            appears_pdf=False,
            policy=(
                make_policy()
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.MANUAL_REVIEW
    )


# ---------------------------------------------------------------------------
# NO ROUTE REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_no_route_requires_review():
    result = (
        resolve_acquisition_decision(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.NONE
            ),
            source_url=None,
            url_verified=False,
            appears_pdf=False,
            policy=(
                make_policy()
            ),
        )
    )

    assert (
        result.decision
        == AcquisitionDecision.MANUAL_REVIEW
    )


