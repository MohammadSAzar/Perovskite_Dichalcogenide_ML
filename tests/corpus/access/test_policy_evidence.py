import pytest

from pydantic import (
    ValidationError,
)

from psk_tmd.corpus.access.policy_evidence import (
    PolicyDecision,
    PolicyEvidenceRecord,
    PolicyProviderType,
    PolicyScope,
)


# ---------------------------------------------------------------------------
# MINIMAL POLICY EVIDENCE
# ---------------------------------------------------------------------------
def test_minimal_policy_evidence():
    evidence = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000001"
            ),
            provider_key=(
                "elsevier"
            ),
            provider_name=(
                "Elsevier"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://example.org/policy"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text=(
                "Research TDM is permitted "
                "subject to stated conditions."
            ),
        )
    )

    assert (
        evidence.provider_key
        == "elsevier"
    )

    assert (
        evidence.scope
        == PolicyScope.TDM
    )

    assert (
        evidence.decision
        == PolicyDecision.CONDITIONAL
    )


# ---------------------------------------------------------------------------
# PROVIDER KEY IS NORMALIZED
# ---------------------------------------------------------------------------
def test_provider_key_is_normalized():
    evidence = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000001"
            ),
            provider_key=(
                " Springer-Nature "
            ),
            provider_name=(
                "Springer Nature"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.UNCLEAR
            ),
            source_url=(
                "https://example.org/policy"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text="Test evidence.",
        )
    )

    assert (
        evidence.provider_key
        == "springer_nature"
    )


# ---------------------------------------------------------------------------
# OPTIONAL TEXT IS NORMALIZED
# ---------------------------------------------------------------------------
def test_optional_text_is_normalized():
    evidence = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000001"
            ),
            provider_key="mdpi",
            provider_name="MDPI",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://example.org/policy"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text=(
                "Automated access is subject "
                "to service conditions."
            ),
            conditions=(
                "  Follow   rate limits.  "
            ),
            notes="   ",
        )
    )

    assert (
        evidence.conditions
        == "Follow rate limits."
    )

    assert (
        evidence.notes
        is None
    )


# ---------------------------------------------------------------------------
# DIFFERENT POLICY SCOPES ARE DISTINCT
# ---------------------------------------------------------------------------
def test_different_policy_scopes_are_distinct():
    tdm = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000001"
            ),
            provider_key="arxiv",
            provider_name="arXiv",
            provider_type=(
                PolicyProviderType.REPOSITORY
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.PERMITTED
            ),
            source_url=(
                "https://example.org/tdm"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text="TDM evidence.",
        )
    )

    automated = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000002"
            ),
            provider_key="arxiv",
            provider_name="arXiv",
            provider_type=(
                PolicyProviderType.REPOSITORY
            ),
            scope=(
                PolicyScope.AUTOMATED_ACCESS
            ),
            decision=(
                PolicyDecision.CONDITIONAL
            ),
            source_url=(
                "https://example.org/access"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text=(
                "Automated access evidence."
            ),
        )
    )

    assert (
        tdm.scope
        != automated.scope
    )


# ---------------------------------------------------------------------------
# AI POLICY IS SEPARATE FROM TDM
# ---------------------------------------------------------------------------
def test_ai_policy_is_separate_from_tdm():
    evidence = (
        PolicyEvidenceRecord(
            evidence_id=(
                "PEV-000001"
            ),
            provider_key="example",
            provider_name=(
                "Example Publisher"
            ),
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.AI_USE
            ),
            decision=(
                PolicyDecision.NOT_PERMITTED
            ),
            source_url=(
                "https://example.org/ai-policy"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text=(
                "AI use is separately "
                "restricted."
            ),
        )
    )

    assert (
        evidence.scope
        == PolicyScope.AI_USE
    )

    assert (
        evidence.decision
        == PolicyDecision.NOT_PERMITTED
    )


# ---------------------------------------------------------------------------
# REQUIRED FIELD CANNOT BE EMPTY
# ---------------------------------------------------------------------------
def test_required_field_cannot_be_empty():
    with pytest.raises(
        ValidationError,
    ):
        PolicyEvidenceRecord(
            evidence_id="   ",
            provider_key="elsevier",
            provider_name="Elsevier",
            provider_type=(
                PolicyProviderType.PUBLISHER
            ),
            scope=(
                PolicyScope.TDM
            ),
            decision=(
                PolicyDecision.UNCLEAR
            ),
            source_url=(
                "https://example.org/policy"
            ),
            observed_date=(
                "2026-08-31"
            ),
            basis_text="Test.",
        )


# ---------------------------------------------------------------------------
# ENUM VALUES
# ---------------------------------------------------------------------------
def test_enum_values():
    assert (
        PolicyProviderType.PUBLISHER.value
        == "publisher"
    )

    assert (
        PolicyProviderType.REPOSITORY.value
        == "repository"
    )

    assert (
        PolicyScope.AUTOMATED_ACCESS.value
        == "automated_access"
    )

    assert (
        PolicyScope.AI_USE.value
        == "ai_use"
    )

    assert (
        PolicyDecision.CONDITIONAL.value
        == "conditional"
    )

