from psk_tmd.corpus.access.combined_policy import (
    CombinedPolicyStatus,
    build_combined_policy_resolution,
    index_provider_evidence_by_scope,
    resolve_automated_access_status,
    resolve_boolean_permission,
    resolve_combined_tdm_status,
)
from psk_tmd.corpus.access.license import (
    normalize_license,
)
from psk_tmd.corpus.access.license_policy import (
    build_license_policy_assessment,
)
from psk_tmd.corpus.access.models import (
    TDMStatus,
)
from psk_tmd.corpus.access.policy import (
    AIUseStatus,
)
from psk_tmd.corpus.access.policy_evidence import (
    PolicyDecision,
    PolicyEvidenceRecord,
    PolicyProviderType,
    PolicyScope,
)


# ---------------------------------------------------------------------------
# MAKE PROVIDER EVIDENCE
# ---------------------------------------------------------------------------
def make_provider_evidence(
    *,
    evidence_id: str,
    scope: PolicyScope,
    decision: PolicyDecision,
) -> PolicyEvidenceRecord:
    return PolicyEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        provider_key="example",
        provider_name=(
            "Example Provider"
        ),
        provider_type=(
            PolicyProviderType.PUBLISHER
        ),
        scope=(
            scope
        ),
        decision=(
            decision
        ),
        source_url=(
            "https://example.org/policy"
        ),
        observed_date=(
            "2026-09-09"
        ),
        basis_text=(
            "Test policy evidence."
        ),
        conditions=(
            "Test condition."
        ),
    )


# ---------------------------------------------------------------------------
# LICENSE PERMITTED TDM STAYS PERMITTED
# ---------------------------------------------------------------------------
def test_license_permitted_tdm_stays_permitted():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        )
    )

    assert (
        resolve_combined_tdm_status(
            license_status=(
                TDMStatus.PERMITTED
            ),
            provider_evidence=(
                evidence
            ),
        )
        == TDMStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# PROVIDER PROHIBITION WINS
# ---------------------------------------------------------------------------
def test_provider_prohibition_wins():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.NOT_PERMITTED
            ),
        )
    )

    assert (
        resolve_combined_tdm_status(
            license_status=(
                TDMStatus.PERMITTED
            ),
            provider_evidence=(
                evidence
            ),
        )
        == TDMStatus.NOT_PERMITTED
    )


# ---------------------------------------------------------------------------
# UNCLEAR LICENSE CAN BE RESOLVED BY PERMITTED POLICY
# ---------------------------------------------------------------------------
def test_unclear_license_can_be_resolved_by_permitted_policy():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.PERMITTED
            ),
        )
    )

    assert (
        resolve_combined_tdm_status(
            license_status=(
                TDMStatus.UNCLEAR
            ),
            provider_evidence=(
                evidence
            ),
        )
        == TDMStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# CONDITIONAL POLICY DOES NOT OVERRIDE UNCLEAR LICENSE
# ---------------------------------------------------------------------------
def test_conditional_policy_does_not_override_unclear_license():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        )
    )

    assert (
        resolve_combined_tdm_status(
            license_status=(
                TDMStatus.UNCLEAR
            ),
            provider_evidence=(
                evidence
            ),
        )
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# CONDITIONAL AUTOMATED ACCESS IS PRESERVED
# ---------------------------------------------------------------------------
def test_conditional_automated_access_is_preserved():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        )
    )

    assert (
        resolve_automated_access_status(
            evidence
        )
        == CombinedPolicyStatus.CONDITIONAL
    )


# ---------------------------------------------------------------------------
# UNKNOWN AUTOMATED ACCESS IS NOT EVALUATED
# ---------------------------------------------------------------------------
def test_unknown_automated_access_is_not_evaluated():
    assert (
        resolve_automated_access_status(
            None
        )
        == CombinedPolicyStatus.NOT_EVALUATED
    )


# ---------------------------------------------------------------------------
# PROVIDER CONDITIONAL LOCAL COPY IS PRESERVED
# ---------------------------------------------------------------------------
def test_provider_conditional_local_copy_is_preserved():
    evidence = (
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.LOCAL_COPY
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        )
    )

    assert (
        resolve_boolean_permission(
            license_permission=True,
            provider_evidence=(
                evidence
            ),
        )
        == CombinedPolicyStatus.CONDITIONAL
    )


# ---------------------------------------------------------------------------
# LICENSE-ONLY REDISTRIBUTION CAN BE PERMITTED
# ---------------------------------------------------------------------------
def test_license_only_redistribution_can_be_permitted():
    assert (
        resolve_boolean_permission(
            license_permission=True,
            provider_evidence=None,
        )
        == CombinedPolicyStatus.PERMITTED
    )


# ---------------------------------------------------------------------------
# BUILD COMBINED CC BY RESOLUTION
# ---------------------------------------------------------------------------
def test_build_combined_cc_by_resolution():
    license_value = (
        normalize_license(
            "CC BY 4.0"
        )
    )

    license_assessment = (
        build_license_policy_assessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            license_value=(
                license_value
            ),
        )
    )

    provider_evidence = [
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        ),
        make_provider_evidence(
            evidence_id="PEV-000002",
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        ),
        make_provider_evidence(
            evidence_id="PEV-000003",
            scope=(
                PolicyScope.LOCAL_COPY
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        ),
    ]

    result = (
        build_combined_policy_resolution(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="example",
            license_assessment=(
                license_assessment
            ),
            provider_evidence_records=(
                provider_evidence
            ),
        )
    )

    assert (
        result.tdm_status
        == TDMStatus.PERMITTED
    )

    assert (
        result.automated_access_status
        == CombinedPolicyStatus.CONDITIONAL
    )

    assert (
        result.local_copy_status
        == CombinedPolicyStatus.CONDITIONAL
    )

    assert (
        result.redistribution_status
        == CombinedPolicyStatus.PERMITTED
    )

    assert (
        result.ai_use_status
        == AIUseStatus.NOT_EVALUATED
    )

    assert (
        result.license_policy_id
        == "POL-000001"
    )

    assert (
        result.provider_evidence_ids
        == [
            "PEV-000001",
            "PEV-000002",
            "PEV-000003",
        ]
    )


# ---------------------------------------------------------------------------
# BUILD WITHOUT LICENSE EVIDENCE
# ---------------------------------------------------------------------------
def test_build_without_license_evidence():
    provider_evidence = [
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
        ),
    ]

    result = (
        build_combined_policy_resolution(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="example",
            license_assessment=None,
            provider_evidence_records=(
                provider_evidence
            ),
        )
    )

    assert (
        result.tdm_status
        == TDMStatus.UNCLEAR
    )

    assert (
        result.license_policy_id
        is None
    )


# ---------------------------------------------------------------------------
# DUPLICATE PROVIDER SCOPE IS REJECTED
# ---------------------------------------------------------------------------
def test_duplicate_provider_scope_is_rejected():
    evidence_records = [
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.PERMITTED
            ),
        ),
        make_provider_evidence(
            evidence_id="PEV-000002",
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.UNCLEAR
            ),
        ),
    ]

    try:
        index_provider_evidence_by_scope(
            evidence_records
        )

    except ValueError:
        return

    raise AssertionError(
        "Expected duplicate provider "
        "policy scope to raise ValueError."
    )


# ---------------------------------------------------------------------------
# PROVIDER AI EVIDENCE IS SEPARATE
# ---------------------------------------------------------------------------
def test_provider_ai_evidence_is_separate():
    provider_evidence = [
        make_provider_evidence(
            evidence_id="PEV-000001",
            scope=(
                PolicyScope.AI_USE
            ),
            decision=(
                PolicyDecision.NOT_PERMITTED
            ),
        ),
    ]

    result = (
        build_combined_policy_resolution(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            provider_key="example",
            license_assessment=None,
            provider_evidence_records=(
                provider_evidence
            ),
        )
    )

    assert (
        result.ai_use_status
        == AIUseStatus.NOT_PERMITTED
    )

    assert (
        result.tdm_status
        == TDMStatus.NOT_EVALUATED
    )

