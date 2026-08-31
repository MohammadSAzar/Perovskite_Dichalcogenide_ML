import pytest

from pydantic import (
    ValidationError,
)

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceSource,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    FullTextFormat,
    TDMStatus,
)
from psk_tmd.corpus.access.resolution import (
    AccessResolutionResult,
    build_access_resolution_result,
    get_evidence_ids,
    validate_evidence_linkage,
)


# ---------------------------------------------------------------------------
# MAKE ACCESS RECORD
# ---------------------------------------------------------------------------
def make_access_record() -> AccessRecord:
    return AccessRecord(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        doi="10.1000/example",
    )


# ---------------------------------------------------------------------------
# MAKE EVIDENCE
# ---------------------------------------------------------------------------
def make_evidence(
    evidence_id: str,
    *,
    access_id: str = "ACC-000001",
    candidate_id: str = "CND-000001",
) -> AccessEvidenceRecord:
    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id=(
            access_id
        ),
        candidate_id=(
            candidate_id
        ),
        evidence_type=(
            AccessEvidenceType.OA_STATUS
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        value="open",
    )


# ---------------------------------------------------------------------------
# MINIMAL RESOLUTION RESULT
# ---------------------------------------------------------------------------
def test_minimal_resolution_result():
    result = AccessResolutionResult(
        access_id="ACC-000001",
        candidate_id="CND-000001",
        proposed_access_status=(
            AccessStatus.REQUIRES_REVIEW
        ),
        proposed_acquisition_route=(
            AcquisitionRoute.NONE
        ),
        proposed_tdm_status=(
            TDMStatus.NOT_EVALUATED
        ),
        reason=(
            "Access evidence has not "
            "been evaluated yet."
        ),
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.evidence_ids
        == ()
    )


# ---------------------------------------------------------------------------
# BUILD RESOLUTION WITH EVIDENCE
# ---------------------------------------------------------------------------
def test_build_resolution_with_evidence():
    access_record = (
        make_access_record()
    )

    evidence = (
        make_evidence(
            "AEV-000001"
        )
    )

    result = (
        build_access_resolution_result(
            access_record,
            [
                evidence
            ],
            proposed_access_status=(
                AccessStatus.AVAILABLE
            ),
            proposed_acquisition_route=(
                AcquisitionRoute.OA_REPOSITORY
            ),
            proposed_tdm_status=(
                TDMStatus.PERMITTED
            ),
            proposed_source_url=(
                "https://example.org/article"
            ),
            proposed_source_version=(
                "version_of_record"
            ),
            proposed_full_text_available=True,
            proposed_full_text_format=(
                FullTextFormat.HTML
            ),
            reason=(
                "Repository evidence "
                "supports lawful full-text access."
            ),
        )
    )

    assert (
        result.access_id
        == "ACC-000001"
    )

    assert (
        result.candidate_id
        == "CND-000001"
    )

    assert (
        result.evidence_ids
        == (
            "AEV-000001",
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.AVAILABLE
    )

    assert (
        result.proposed_full_text_available
        is True
    )


# ---------------------------------------------------------------------------
# ACCESS ID LINKAGE MUST MATCH
# ---------------------------------------------------------------------------
def test_access_id_linkage_must_match():
    access_record = (
        make_access_record()
    )

    evidence = (
        make_evidence(
            "AEV-000001",
            access_id="ACC-999999",
        )
    )

    with pytest.raises(
        ValueError,
        match="access_id",
    ):
        validate_evidence_linkage(
            access_record,
            [
                evidence
            ],
        )


# ---------------------------------------------------------------------------
# CANDIDATE ID LINKAGE MUST MATCH
# ---------------------------------------------------------------------------
def test_candidate_id_linkage_must_match():
    access_record = (
        make_access_record()
    )

    evidence = (
        make_evidence(
            "AEV-000001",
            candidate_id="CND-999999",
        )
    )

    with pytest.raises(
        ValueError,
        match="candidate_id",
    ):
        validate_evidence_linkage(
            access_record,
            [
                evidence
            ],
        )


# ---------------------------------------------------------------------------
# DUPLICATE EVIDENCE IDS FAIL
# ---------------------------------------------------------------------------
def test_duplicate_evidence_ids_fail():
    first = (
        make_evidence(
            "AEV-000001"
        )
    )

    second = (
        make_evidence(
            "AEV-000001"
        )
    )

    with pytest.raises(
        ValueError,
        match="Duplicate",
    ):
        get_evidence_ids(
            [
                first,
                second,
            ]
        )


# ---------------------------------------------------------------------------
# FORMAT REQUIRES FULL TEXT
# ---------------------------------------------------------------------------
def test_format_requires_full_text():
    with pytest.raises(
        ValidationError,
        match=(
            "proposed_full_text_format "
            "requires "
            "proposed_full_text_available=True"
        ),
    ):
        AccessResolutionResult(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                AcquisitionRoute.NONE
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            proposed_full_text_available=False,
            proposed_full_text_format=(
                FullTextFormat.PDF
            ),
            reason="Test reason.",
        )


# ---------------------------------------------------------------------------
# REQUIRED REASON MUST NOT BE EMPTY
# ---------------------------------------------------------------------------
def test_required_reason_must_not_be_empty():
    with pytest.raises(
        ValidationError,
    ):
        AccessResolutionResult(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                AcquisitionRoute.NONE
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            reason="   ",
        )


# ---------------------------------------------------------------------------
# DUPLICATE RESULT EVIDENCE IDS FAIL
# ---------------------------------------------------------------------------
def test_duplicate_result_evidence_ids_fail():
    with pytest.raises(
        ValidationError,
        match="must be unique",
    ):
        AccessResolutionResult(
            access_id="ACC-000001",
            candidate_id="CND-000001",
            proposed_access_status=(
                AccessStatus.REQUIRES_REVIEW
            ),
            proposed_acquisition_route=(
                AcquisitionRoute.NONE
            ),
            proposed_tdm_status=(
                TDMStatus.NOT_EVALUATED
            ),
            evidence_ids=(
                "AEV-000001",
                "AEV-000001",
            ),
            reason="Test reason.",
        )


