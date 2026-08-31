import pytest

from pydantic import (
    ValidationError,
)

from psk_tmd.corpus.access.evidence import (
    AccessEvidenceRecord,
    AccessEvidenceSource,
    AccessEvidenceType,
)


# ---------------------------------------------------------------------------
# MINIMAL EVIDENCE RECORD
# ---------------------------------------------------------------------------
def test_minimal_evidence_record():
    record = AccessEvidenceRecord(
        evidence_id="AEV-000001",
        access_id="ACC-000001",
        candidate_id="CND-000001",
        evidence_type=(
            AccessEvidenceType.OA_STATUS
        ),
        source=(
            AccessEvidenceSource.OPENALEX
        ),
    )

    assert (
        record.evidence_type
        == AccessEvidenceType.OA_STATUS
    )

    assert (
        record.source
        == AccessEvidenceSource.OPENALEX
    )


# ---------------------------------------------------------------------------
# NORMALIZE OPTIONAL TEXT
# ---------------------------------------------------------------------------
def test_normalize_optional_text():
    record = AccessEvidenceRecord(
        evidence_id="AEV-000001",
        access_id="ACC-000001",
        candidate_id="CND-000001",
        evidence_type=(
            AccessEvidenceType.LICENSE
        ),
        source=(
            AccessEvidenceSource.PUBLISHER
        ),
        source_name=(
            "  Example   Publisher  "
        ),
        notes="   ",
    )

    assert (
        record.source_name
        == "Example Publisher"
    )

    assert (
        record.notes
        is None
    )


# ---------------------------------------------------------------------------
# FULL EVIDENCE RECORD
# ---------------------------------------------------------------------------
def test_full_evidence_record():
    record = AccessEvidenceRecord(
        evidence_id="AEV-000001",
        access_id="ACC-000001",
        candidate_id="CND-000001",
        evidence_type=(
            AccessEvidenceType.TDM_PERMISSION
        ),
        source=(
            AccessEvidenceSource.PUBLISHER
        ),
        source_name="Example Publisher",
        source_url=(
            "https://example.org/tdm"
        ),
        value="permitted",
        basis=(
            "Publisher terms explicitly "
            "permit research TDM."
        ),
        observed_date="2026-08-31",
        notes="Checked manually.",
    )

    assert (
        record.value
        == "permitted"
    )

    assert (
        record.observed_date.isoformat()
        == "2026-08-31"
    )


# ---------------------------------------------------------------------------
# REQUIRED IDS MUST NOT BE EMPTY
# ---------------------------------------------------------------------------
def test_required_ids_must_not_be_empty():
    with pytest.raises(
        ValidationError,
    ):
        AccessEvidenceRecord(
            evidence_id="   ",
            access_id="ACC-000001",
            candidate_id="CND-000001",
            evidence_type=(
                AccessEvidenceType.OA_STATUS
            ),
            source=(
                AccessEvidenceSource.CROSSREF
            ),
        )


# ---------------------------------------------------------------------------
# ENUM VALUES
# ---------------------------------------------------------------------------
def test_enum_values():
    assert (
        AccessEvidenceType.LICENSE.value
        == "license"
    )

    assert (
        AccessEvidenceType.TDM_PERMISSION.value
        == "tdm_permission"
    )

    assert (
        AccessEvidenceSource.REPOSITORY.value
        == "repository"
    )

