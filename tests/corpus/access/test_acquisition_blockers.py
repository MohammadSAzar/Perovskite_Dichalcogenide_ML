from psk_tmd.corpus.access.acquisition_blockers import (
    AcquisitionBlockerType,
    assess_acquisition_blockers,
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
    automated_status: (
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
            automated_status
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
# READY RECORD HAS NO BLOCKERS
# ---------------------------------------------------------------------------
def test_ready_record_has_no_blockers():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy()
            ),
        )
    )

    assert (
        result.is_blocked
        is False
    )

    assert (
        result.blockers
        == []
    )


# ---------------------------------------------------------------------------
# MULTIPLE BLOCKERS ARE PRESERVED
# ---------------------------------------------------------------------------
def test_multiple_blockers_are_preserved():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.NONE
            ),
            url_verified=False,
            appears_pdf=False,
            policy=(
                make_policy(
                    tdm_status=(
                        TDMStatus.UNCLEAR
                    ),
                    automated_status=(
                        CombinedPolicyStatus.UNCLEAR
                    ),
                    local_copy_status=(
                        CombinedPolicyStatus.NOT_EVALUATED
                    ),
                )
            ),
        )
    )

    blocker_types = {
        blocker.blocker_type
        for blocker
        in result.blockers
    }

    assert (
        AcquisitionBlockerType.NO_ROUTE
        in blocker_types
    )

    assert (
        AcquisitionBlockerType.TDM_UNRESOLVED
        in blocker_types
    )

    assert (
        (
            AcquisitionBlockerType
            .AUTOMATED_ACCESS_UNRESOLVED
        )
        in blocker_types
    )

    assert (
        (
            AcquisitionBlockerType
            .LOCAL_COPY_UNRESOLVED
        )
        in blocker_types
    )

    assert (
        AcquisitionBlockerType.URL_NOT_VERIFIED
        in blocker_types
    )

    assert (
        AcquisitionBlockerType.PDF_NOT_VERIFIED
        in blocker_types
    )


# ---------------------------------------------------------------------------
# CONDITIONAL POLICY IS NOT A BLOCKER
# ---------------------------------------------------------------------------
def test_conditional_policy_is_not_a_blocker():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    automated_status=(
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
        result.is_blocked
        is False
    )


# ---------------------------------------------------------------------------
# UNCLEAR AUTOMATED ACCESS IS A BLOCKER
# ---------------------------------------------------------------------------
def test_unclear_automated_access_is_a_blocker():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    automated_status=(
                        CombinedPolicyStatus.UNCLEAR
                    )
                )
            ),
        )
    )

    blocker_types = [
        blocker.blocker_type
        for blocker
        in result.blockers
    ]

    assert (
        (
            AcquisitionBlockerType
            .AUTOMATED_ACCESS_UNRESOLVED
        )
        in blocker_types
    )


# ---------------------------------------------------------------------------
# UNRESOLVED TDM IS A BLOCKER
# ---------------------------------------------------------------------------
def test_unresolved_tdm_is_a_blocker():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            url_verified=True,
            appears_pdf=True,
            policy=(
                make_policy(
                    tdm_status=(
                        TDMStatus.NOT_EVALUATED
                    )
                )
            ),
        )
    )

    blocker_types = [
        blocker.blocker_type
        for blocker
        in result.blockers
    ]

    assert (
        AcquisitionBlockerType.TDM_UNRESOLVED
        in blocker_types
    )


# ---------------------------------------------------------------------------
# NOT PERMITTED TDM IS DISTINCT
# ---------------------------------------------------------------------------
def test_not_permitted_tdm_is_distinct():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.OA_REPOSITORY
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

    blocker_types = [
        blocker.blocker_type
        for blocker
        in result.blockers
    ]

    assert (
        AcquisitionBlockerType.TDM_NOT_PERMITTED
        in blocker_types
    )

    assert (
        AcquisitionBlockerType.TDM_UNRESOLVED
        not in blocker_types
    )


# ---------------------------------------------------------------------------
# UNVERIFIED URL AND PDF ARE DISTINCT
# ---------------------------------------------------------------------------
def test_unverified_url_and_pdf_are_distinct():
    result = (
        assess_acquisition_blockers(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            route=(
                AcquisitionRoute.PUBLISHER_DOWNLOAD
            ),
            url_verified=False,
            appears_pdf=False,
            policy=(
                make_policy()
            ),
        )
    )

    blocker_types = {
        blocker.blocker_type
        for blocker
        in result.blockers
    }

    assert (
        AcquisitionBlockerType.URL_NOT_VERIFIED
        in blocker_types
    )

    assert (
        AcquisitionBlockerType.PDF_NOT_VERIFIED
        in blocker_types
    )

