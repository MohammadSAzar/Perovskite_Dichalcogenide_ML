from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    MechanismLabel,
)
from psk_tmd.corpus.extraction import (
    MechanismEvidenceCandidate,
    MechanismExtractionResult,
)
from psk_tmd.common.models import (
    MechanismAssessment,
    MechanismEvidence,
)


# ---------------------------------------------------------------------------
# MECHANISM RECORD BUILD RESULT
# ---------------------------------------------------------------------------
class MechanismRecordBuildResult(BaseModel):
    mechanism_assessment: MechanismAssessment

    mechanism_evidence: list[
        MechanismEvidence
    ] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# NORMALIZE EVIDENCE TYPE
# ---------------------------------------------------------------------------
def normalize_evidence_type(
    evidence_type: str,
) -> tuple[
    EvidenceType,
    str | None,
]:
    try:
        normalized_type = EvidenceType(
            evidence_type
        )

        return (
            normalized_type,
            None,
        )

    except ValueError:
        return (
            EvidenceType.UNKNOWN,
            evidence_type,
        )


# ---------------------------------------------------------------------------
# BUILD SOURCE LOCATION
# ---------------------------------------------------------------------------
def build_source_location(
    candidate: MechanismEvidenceCandidate,
) -> str | None:
    parts: list[str] = []

    if candidate.page_number is not None:
        parts.append(
            f"page {candidate.page_number}"
        )

    if candidate.section_title:
        parts.append(
            candidate.section_title
        )

    elif candidate.section_role:
        parts.append(
            candidate.section_role.value
        )

    if not parts:
        return None

    return "; ".join(
        parts
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM ASSESSMENT
# ---------------------------------------------------------------------------
def build_mechanism_assessment(
    extraction_result: MechanismExtractionResult,
    mechanism_assessment_id: str,
    sample_id: str,
    applies_to_series_id: str | None = None,
) -> MechanismAssessment:
    if extraction_result.mechanism_claims:
        claim = (
            extraction_result.mechanism_claims[
                0
            ]
        )

        return MechanismAssessment(
            mechanism_assessment_id=(
                mechanism_assessment_id
            ),
            sample_id=sample_id,
            applies_to_series_id=(
                applies_to_series_id
            ),
            mechanism_reported=(
                claim.mechanism_reported
            ),
            mechanism_normalized=(
                claim.mechanism_normalized
            ),
            charge_transfer_class=None,
            claim_explicit=(
                claim.claim_explicit
            ),
            assessment_confidence=None,
            reviewer_notes=None,
        )

    return MechanismAssessment(
        mechanism_assessment_id=(
            mechanism_assessment_id
        ),
        sample_id=sample_id,
        applies_to_series_id=(
            applies_to_series_id
        ),
        mechanism_reported=None,
        mechanism_normalized=(
            MechanismLabel.UNKNOWN
        ),
        charge_transfer_class=None,
        claim_explicit=False,
        assessment_confidence=None,
        reviewer_notes=None,
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def build_mechanism_evidence(
    candidate: MechanismEvidenceCandidate,
    evidence_id: str,
    mechanism_assessment_id: str,
) -> MechanismEvidence:
    (
        evidence_type,
        evidence_subtype,
    ) = normalize_evidence_type(
        candidate.evidence_type
    )

    return MechanismEvidence(
        evidence_id=evidence_id,
        mechanism_assessment_id=(
            mechanism_assessment_id
        ),
        evidence_type=evidence_type,
        evidence_subtype=(
            evidence_subtype
        ),
        support=(
            EvidenceSupport.UNKNOWN
        ),
        evidence_strength=(
            EvidenceStrength.UNKNOWN
        ),
        reported_result=(
            candidate.source_text
        ),
        source_location=(
            build_source_location(
                candidate
            )
        ),
        notes=None,
        characterization_role=(
            candidate.characterization_role
        ),
        mechanism_discriminating=(
            candidate.mechanism_discriminating
        ),
        requires_context=(
            candidate.requires_context
        ),
        required_context=(
            candidate.required_context
        ),
        section_role=(
            candidate.section_role
        ),
        section_title=(
            candidate.section_title
        ),
        page_number=(
            candidate.page_number
        ),
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM RECORDS
# ---------------------------------------------------------------------------
def build_mechanism_records(
    extraction_result: MechanismExtractionResult,
    mechanism_assessment_id: str,
    evidence_ids: list[str],
    sample_id: str,
    applies_to_series_id: str | None = None,
) -> MechanismRecordBuildResult:
    evidence_candidates = (
        extraction_result
        .mechanism_evidence_candidates
    )

    if (
        len(evidence_ids)
        != len(evidence_candidates)
    ):
        raise ValueError(
            "The number of evidence IDs "
            "must match the number of "
            "mechanism evidence candidates."
        )

    mechanism_assessment = (
        build_mechanism_assessment(
            extraction_result=(
                extraction_result
            ),
            mechanism_assessment_id=(
                mechanism_assessment_id
            ),
            sample_id=sample_id,
            applies_to_series_id=(
                applies_to_series_id
            ),
        )
    )

    mechanism_evidence = [
        build_mechanism_evidence(
            candidate=candidate,
            evidence_id=evidence_id,
            mechanism_assessment_id=(
                mechanism_assessment_id
            ),
        )
        for candidate, evidence_id
        in zip(
            evidence_candidates,
            evidence_ids,
        )
    ]

    return MechanismRecordBuildResult(
        mechanism_assessment=(
            mechanism_assessment
        ),
        mechanism_evidence=(
            mechanism_evidence
        ),
    )


