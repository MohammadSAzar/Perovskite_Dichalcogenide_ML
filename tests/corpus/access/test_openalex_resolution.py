import pytest

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceSource,
    AccessEvidenceType,
)
from psk_tmd.corpus.access.models import (
    AccessRecord,
    AccessStatus,
    AcquisitionRoute,
    TDMStatus,
)
from psk_tmd.corpus.access.openalex_resolution import (
    get_evidence_by_type,
    get_single_evidence,
    normalize_oa_status,
    propose_openalex_resolution,
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
    evidence_type: AccessEvidenceType,
    *,
    value: str | None = None,
    source_url: str | None = None,
) -> AccessEvidenceRecord:
    return AccessEvidenceRecord(
        evidence_id=(
            evidence_id
        ),
        access_id="ACC-000001",
        candidate_id="CND-000001",
        evidence_type=(
            evidence_type
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
        source_name="OpenAlex",
        source_url=(
            source_url
        ),
        value=(
            value
        ),
    )


# ---------------------------------------------------------------------------
# GET EVIDENCE BY TYPE
# ---------------------------------------------------------------------------
def test_get_evidence_by_type():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="gold",
        ),
        make_evidence(
            "AEV-000002",
            AccessEvidenceType.LICENSE,
            value="cc-by",
        ),
    ]

    result = (
        get_evidence_by_type(
            evidence,
            AccessEvidenceType.LICENSE,
        )
    )

    assert len(
        result
    ) == 1

    assert (
        result[
            0
        ].evidence_id
        == "AEV-000002"
    )


# ---------------------------------------------------------------------------
# GET SINGLE EVIDENCE
# ---------------------------------------------------------------------------
def test_get_single_evidence():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="gold",
        )
    ]

    result = (
        get_single_evidence(
            evidence,
            AccessEvidenceType.OA_STATUS,
        )
    )

    assert result is not None

    assert (
        result.value
        == "gold"
    )


# ---------------------------------------------------------------------------
# DUPLICATE SINGLE EVIDENCE FAILS
# ---------------------------------------------------------------------------
def test_duplicate_single_evidence_fails():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="gold",
        ),
        make_evidence(
            "AEV-000002",
            AccessEvidenceType.OA_STATUS,
            value="green",
        ),
    ]

    with pytest.raises(
        ValueError,
        match="at most one",
    ):
        get_single_evidence(
            evidence,
            AccessEvidenceType.OA_STATUS,
        )


# ---------------------------------------------------------------------------
# NORMALIZE OA STATUS
# ---------------------------------------------------------------------------
def test_normalize_oa_status():
    evidence = (
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="  GOLD  ",
        )
    )

    assert (
        normalize_oa_status(
            evidence
        )
        == "gold"
    )


# ---------------------------------------------------------------------------
# CLOSED BECOMES METADATA ONLY
# ---------------------------------------------------------------------------
def test_closed_becomes_metadata_only():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="closed",
        )
    ]

    result = (
        propose_openalex_resolution(
            make_access_record(),
            evidence,
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.METADATA_ONLY
    )

    assert (
        result.proposed_acquisition_route
        == AcquisitionRoute.NONE
    )

    assert (
        result.proposed_tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        result.proposed_full_text_available
        is False
    )


# ---------------------------------------------------------------------------
# GOLD WITH LOCATION REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_gold_with_location_requires_review():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="gold",
        ),
        make_evidence(
            "AEV-000002",
            AccessEvidenceType.FULL_TEXT_LOCATION,
            value="oa_location",
            source_url=(
                "https://example.org/article.pdf"
            ),
        ),
        make_evidence(
            "AEV-000003",
            AccessEvidenceType.VERSION,
            value="publishedVersion",
        ),
        make_evidence(
            "AEV-000004",
            AccessEvidenceType.LICENSE,
            value="cc-by",
        ),
    ]

    result = (
        propose_openalex_resolution(
            make_access_record(),
            evidence,
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.proposed_acquisition_route
        == AcquisitionRoute.NONE
    )

    assert (
        result.proposed_tdm_status
        == TDMStatus.NOT_EVALUATED
    )

    assert (
        result.proposed_source_url
        == "https://example.org/article.pdf"
    )

    assert (
        result.proposed_source_version
        == "publishedVersion"
    )

    assert (
        result.proposed_full_text_available
        is False
    )


# ---------------------------------------------------------------------------
# GREEN WITH LOCATION REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_green_with_location_requires_review():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="green",
        ),
        make_evidence(
            "AEV-000002",
            AccessEvidenceType.FULL_TEXT_LOCATION,
            source_url=(
                "https://repository.example/"
                "article.pdf"
            ),
        ),
    ]

    result = (
        propose_openalex_resolution(
            make_access_record(),
            evidence,
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.proposed_source_url
        == (
            "https://repository.example/"
            "article.pdf"
        )
    )


# ---------------------------------------------------------------------------
# NON-CLOSED WITHOUT LOCATION REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_nonclosed_without_location_requires_review():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="gold",
        )
    ]

    result = (
        propose_openalex_resolution(
            make_access_record(),
            evidence,
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.proposed_source_url
        is None
    )


# ---------------------------------------------------------------------------
# UNKNOWN STATUS REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_unknown_status_requires_review():
    evidence = [
        make_evidence(
            "AEV-000001",
            AccessEvidenceType.OA_STATUS,
            value="unknown",
        )
    ]

    result = (
        propose_openalex_resolution(
            make_access_record(),
            evidence,
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )


# ---------------------------------------------------------------------------
# NO EVIDENCE REQUIRES REVIEW
# ---------------------------------------------------------------------------
def test_no_evidence_requires_review():
    result = (
        propose_openalex_resolution(
            make_access_record(),
            [],
        )
    )

    assert (
        result.proposed_access_status
        == AccessStatus.REQUIRES_REVIEW
    )

    assert (
        result.evidence_ids
        == ()
    )


