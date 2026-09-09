import pytest

from pydantic import (
    ValidationError,
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
# MINIMAL POLICY ASSESSMENT
# ---------------------------------------------------------------------------
def test_minimal_policy_assessment():
    assessment = (
        TDMPolicyAssessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            basis_type=(
                PolicyBasisType.UNKNOWN
            ),
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        assessment.ai_use_status
        == AIUseStatus.NOT_EVALUATED
    )

    assert (
        assessment.basis_type
        == PolicyBasisType.UNKNOWN
    )


# ---------------------------------------------------------------------------
# FULL POLICY ASSESSMENT
# ---------------------------------------------------------------------------
def test_full_policy_assessment():
    assessment = (
        TDMPolicyAssessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.PERMITTED
            ),
            ai_use_status=(
                AIUseStatus.UNCLEAR
            ),
            basis_type=(
                PolicyBasisType.PUBLISHER_TDM_TERMS
            ),
            license_name="CC BY 4.0",
            policy_url=(
                "https://example.org/"
                "tdm-policy"
            ),
            jurisdiction="Iran",
            basis_text=(
                "Publisher terms explicitly "
                "permit research TDM."
            ),
            automated_access_permitted=True,
            local_copy_permitted=True,
            redistribution_permitted=False,
            notes=(
                "AI use evaluated separately."
            ),
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.PERMITTED
    )

    assert (
        assessment.ai_use_status
        == AIUseStatus.UNCLEAR
    )

    assert (
        assessment
        .automated_access_permitted
        is True
    )

    assert (
        assessment
        .redistribution_permitted
        is False
    )


# ---------------------------------------------------------------------------
# TDM AND AI STATUS ARE INDEPENDENT
# ---------------------------------------------------------------------------
def test_tdm_and_ai_status_are_independent():
    assessment = (
        TDMPolicyAssessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.PERMITTED
            ),
            ai_use_status=(
                AIUseStatus.NOT_PERMITTED
            ),
            basis_type=(
                PolicyBasisType.CONTRACT_TERMS
            ),
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.PERMITTED
    )

    assert (
        assessment.ai_use_status
        == AIUseStatus.NOT_PERMITTED
    )


# ---------------------------------------------------------------------------
# POLICY CAN BE UNCLEAR
# ---------------------------------------------------------------------------
def test_policy_can_be_unclear():
    assessment = (
        TDMPolicyAssessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.UNCLEAR
            ),
            basis_type=(
                PolicyBasisType.LICENSE_TERMS
            ),
            license_name="cc-by-nc-nd",
        )
    )

    assert (
        assessment.tdm_status
        == TDMStatus.UNCLEAR
    )


# ---------------------------------------------------------------------------
# OPTIONAL TEXT IS NORMALIZED
# ---------------------------------------------------------------------------
def test_optional_text_is_normalized():
    assessment = (
        TDMPolicyAssessment(
            policy_id="POL-000001",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            basis_type=(
                PolicyBasisType.UNKNOWN
            ),
            license_name=(
                "  CC   BY  4.0  "
            ),
            notes="   ",
        )
    )

    assert (
        assessment.license_name
        == "CC BY 4.0"
    )

    assert (
        assessment.notes
        is None
    )


# ---------------------------------------------------------------------------
# REQUIRED POLICY ID CANNOT BE EMPTY
# ---------------------------------------------------------------------------
def test_required_policy_id_cannot_be_empty():
    with pytest.raises(
        ValidationError,
    ):
        TDMPolicyAssessment(
            policy_id="   ",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            basis_type=(
                PolicyBasisType.UNKNOWN
            ),
        )


# ---------------------------------------------------------------------------
# ENUM VALUES
# ---------------------------------------------------------------------------
def test_enum_values():
    assert (
        PolicyBasisType.LICENSE_TERMS.value
        == "license_terms"
    )

    assert (
        PolicyBasisType.PUBLISHER_TDM_TERMS.value
        == "publisher_tdm_terms"
    )

    assert (
        AIUseStatus.PERMITTED.value
        == "permitted"
    )

    assert (
        AIUseStatus.NOT_EVALUATED.value
        == "not_evaluated"
    )

