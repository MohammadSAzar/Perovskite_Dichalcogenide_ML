import pytest

from psk_tmd.common.constants import (
    CharacterizationRole,
    EvidenceContextType,
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    LabelStatus,
    ManualReviewStatus,
    MechanismLabel,
    PaperSectionRole, ChargeTransferClass,
)
from psk_tmd.corpus.builders import (
    build_mechanism_assessment,
    build_mechanism_evidence,
    build_mechanism_records,
    build_pair_record,
    build_source_location,
    normalize_evidence_type,
    build_pair_mechanism_label,
)
from psk_tmd.corpus.extraction import (
    MechanismClaimCandidate,
    MechanismEvidenceCandidate,
    MechanismExtractionResult,
)
from psk_tmd.corpus.pair_extraction import (
    PairCandidate,
    PairExtractionResult,
)
from psk_tmd.corpus.mechanism_aggregation import PairMechanismAggregationResult


# ---------------------------------------------------------------------------
# BUILD PAIR RECORD
# ---------------------------------------------------------------------------
def test_build_pair_record():
    extraction_result = (
        PairExtractionResult(
            primary_pair_candidate=(
                PairCandidate(
                    psk_formula_reported=(
                        "CaTiO3"
                    ),
                    tmd_formula_reported=(
                        "WS2"
                    ),
                    page_number=5,
                    section_title=(
                        "Results and discussion"
                    ),
                    section_role=(
                        PaperSectionRole.RESULTS
                    ),
                    source_text=(
                        "The CaTiO3/WS2 "
                        "heterostructure was "
                        "constructed."
                    ),
                    score=12.0,
                )
            ),
            pair_candidates=[],
        )
    )

    pair = build_pair_record(
        extraction_result=(
            extraction_result
        ),
        pair_id="PAIR-0001",
    )

    assert pair is not None

    assert (
        pair.pair_id
        == "PAIR-0001"
    )

    assert (
        pair.psk_formula_reported
        == "CaTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# PAIR BUILDER DOES NOT NORMALIZE FORMULAS
# ---------------------------------------------------------------------------
def test_pair_builder_does_not_normalize_formulas():
    extraction_result = (
        PairExtractionResult(
            primary_pair_candidate=(
                PairCandidate(
                    psk_formula_reported=(
                        "La0.8Sr0.2FeO3"
                    ),
                    tmd_formula_reported=(
                        "MoS1.8Se0.2"
                    ),
                    page_number=1,
                    section_title=None,
                    section_role=(
                        PaperSectionRole.ABSTRACT
                    ),
                    source_text=(
                        "The "
                        "La0.8Sr0.2FeO3/"
                        "MoS1.8Se0.2 "
                        "heterostructure was "
                        "prepared."
                    ),
                    score=11.0,
                )
            ),
            pair_candidates=[],
        )
    )

    pair = build_pair_record(
        extraction_result=(
            extraction_result
        ),
        pair_id="PAIR-0002",
    )

    assert pair is not None

    assert (
        pair.psk_formula_reported
        == "La0.8Sr0.2FeO3"
    )

    assert (
        pair.tmd_formula_reported
        == "MoS1.8Se0.2"
    )

    assert (
        pair.psk_formula_normalized
        is None
    )

    assert (
        pair.tmd_formula_normalized
        is None
    )


# ---------------------------------------------------------------------------
# BUILD PAIR RECORD USES PRIMARY CANDIDATE
# ---------------------------------------------------------------------------
def test_build_pair_record_uses_primary_candidate():
    primary_candidate = PairCandidate(
        psk_formula_reported=(
            "CaTiO3"
        ),
        tmd_formula_reported=(
            "WS2"
        ),
        page_number=9,
        section_title=(
            "Possible photocatalytic mechanism"
        ),
        section_role=(
            PaperSectionRole.MECHANISM
        ),
        source_text=(
            "The CaTiO3/WS2 "
            "heterostructure was studied."
        ),
        score=13.5,
    )

    cited_candidate = PairCandidate(
        psk_formula_reported=(
            "CaTiO3"
        ),
        tmd_formula_reported=(
            "MoS2"
        ),
        page_number=2,
        section_title=(
            "Introduction"
        ),
        section_role=(
            PaperSectionRole.INTRODUCTION
        ),
        source_text=(
            "Previous work reported "
            "MoS2/CaTiO3."
        ),
        score=10.5,
    )

    extraction_result = (
        PairExtractionResult(
            primary_pair_candidate=(
                primary_candidate
            ),
            pair_candidates=[
                primary_candidate,
                cited_candidate,
            ],
        )
    )

    pair = build_pair_record(
        extraction_result=(
            extraction_result
        ),
        pair_id="PAIR-0003",
    )

    assert pair is not None

    assert (
        pair.psk_formula_reported
        == "CaTiO3"
    )

    assert (
        pair.tmd_formula_reported
        == "WS2"
    )


# ---------------------------------------------------------------------------
# BUILD PAIR MECHANISM LABEL
# ---------------------------------------------------------------------------
def test_build_pair_mechanism_label():
    aggregation_result = (
        PairMechanismAggregationResult(
            pair_id="PAIR-0001",
            assessment_ids=[
                "MEA-0001",
            ],
            mechanism_labels=[
                MechanismLabel.Z_SCHEME,
            ],
            charge_transfer_classes=[
                ChargeTransferClass
                .MEDIATED_RECOMBINATION,
            ],
            mechanism_consensus=(
                MechanismLabel.Z_SCHEME
            ),
            charge_transfer_consensus=(
                ChargeTransferClass
                .MEDIATED_RECOMBINATION
            ),
            has_disagreement=False,
        )
    )

    label = build_pair_mechanism_label(
        aggregation_result
    )

    assert (
        label.pair_id
        == "PAIR-0001"
    )

    assert (
        label.source_assessment_ids
        == [
            "MEA-0001"
        ]
    )

    assert (
        label.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        label.charge_transfer_class
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )

    assert (
        label.has_disagreement
        is False
    )

    assert (
        label.manual_review_status
        == ManualReviewStatus.PENDING
    )

    assert (
        label.label_status
        == LabelStatus.PENDING_REVIEW
    )


# ---------------------------------------------------------------------------
# BUILD DISAGREED PAIR MECHANISM LABEL
# ---------------------------------------------------------------------------
def test_build_disagreed_pair_mechanism_label():
    aggregation_result = (
        PairMechanismAggregationResult(
            pair_id="PAIR-0001",
            assessment_ids=[
                "MEA-0001",
                "MEA-0002",
            ],
            mechanism_labels=[
                MechanismLabel.Z_SCHEME,
                MechanismLabel.TYPE_II,
            ],
            charge_transfer_classes=[
                ChargeTransferClass
                .MEDIATED_RECOMBINATION,
                ChargeTransferClass.TYPE_II,
            ],
            mechanism_consensus=None,
            charge_transfer_consensus=None,
            has_disagreement=True,
        )
    )

    label = build_pair_mechanism_label(
        aggregation_result
    )

    assert (
        label.mechanism_normalized
        is None
    )

    assert (
        label.charge_transfer_class
        is None
    )

    assert (
        label.has_disagreement
        is True
    )

    assert (
        label.label_status
        == LabelStatus.PENDING_REVIEW
    )


# ---------------------------------------------------------------------------
# NO PAIR RECORD WITHOUT PRIMARY CANDIDATE
# ---------------------------------------------------------------------------
def test_no_pair_record_without_primary_candidate():
    extraction_result = (
        PairExtractionResult(
            primary_pair_candidate=None,
            pair_candidates=[],
        )
    )

    pair = build_pair_record(
        extraction_result=(
            extraction_result
        ),
        pair_id="PAIR-0004",
    )

    assert pair is None


# ---------------------------------------------------------------------------
# MAKE Z-SCHEME EXTRACTION RESULT
# ---------------------------------------------------------------------------
def make_z_scheme_extraction_result(
) -> MechanismExtractionResult:
    return MechanismExtractionResult(
        mechanism_claims=[
            MechanismClaimCandidate(
                mechanism_reported=(
                    "Z-scheme"
                ),
                mechanism_normalized=(
                    MechanismLabel.Z_SCHEME
                ),
                charge_transfer_class=None,
                claim_explicit=True,
                page_number=9,
                section_title=(
                    "3.5. Possible "
                    "photocatalytic mechanism"
                ),
                section_role=(
                    PaperSectionRole.MECHANISM
                ),
                source_text=(
                    "The Z-scheme mechanism "
                    "was proposed."
                ),
                score=7.0,
            ),
        ],
        characterization_candidates=[],
        mechanism_evidence_candidates=[
            MechanismEvidenceCandidate(
                evidence_type=(
                    "radical_trapping"
                ),
                characterization_role=(
                    CharacterizationRole.MECHANISM_ASSESSMENT
                ),
                mechanism_discriminating=True,
                requires_context=True,
                required_context=[
                    EvidenceContextType.BAND_EDGES,
                    EvidenceContextType.REDOX_POTENTIALS,
                ],
                page_number=9,
                section_title=(
                    "3.5. Possible "
                    "photocatalytic mechanism"
                ),
                section_role=(
                    PaperSectionRole.MECHANISM
                ),
                matched_terms=[
                    "scavenger",
                    "active species",
                ],
                source_text=(
                    "Active-species trapping "
                    "experiments identified "
                    "the predominant radicals."
                ),
                score=20.0,
            ),
            MechanismEvidenceCandidate(
                evidence_type=(
                    "band_alignment"
                ),
                characterization_role=(
                    CharacterizationRole.BAND_STRUCTURE
                ),
                mechanism_discriminating=False,
                requires_context=False,
                required_context=[],
                page_number=9,
                section_title=(
                    "3.6. Photocatalytic "
                    "mechanism"
                ),
                section_role=(
                    PaperSectionRole.MECHANISM
                ),
                matched_terms=[
                    "conduction band",
                    "valence band",
                ],
                source_text=(
                    "The conduction-band and "
                    "valence-band positions "
                    "were used to interpret "
                    "the observed radicals."
                ),
                score=10.0,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# NORMALIZE KNOWN EVIDENCE TYPE
# ---------------------------------------------------------------------------
def test_normalize_known_evidence_type():
    evidence_type = next(
        iter(
            EvidenceType
        )
    )

    normalized, subtype = (
        normalize_evidence_type(
            evidence_type.value
        )
    )

    assert (
        normalized
        == evidence_type
    )

    assert (
        subtype
        is None
    )


# ---------------------------------------------------------------------------
# NORMALIZE UNKNOWN EVIDENCE TYPE
# ---------------------------------------------------------------------------
def test_normalize_unknown_evidence_type():
    normalized, subtype = (
        normalize_evidence_type(
            "custom_technique"
        )
    )

    assert (
        normalized
        == EvidenceType.UNKNOWN
    )

    assert (
        subtype
        == "custom_technique"
    )


# ---------------------------------------------------------------------------
# BUILD SOURCE LOCATION
# ---------------------------------------------------------------------------
def test_build_source_location():
    candidate = (
        make_z_scheme_extraction_result()
        .mechanism_evidence_candidates[
            0
        ]
    )

    location = build_source_location(
        candidate
    )

    assert (
        location
        == (
            "page 9; "
            "3.5. Possible "
            "photocatalytic mechanism"
        )
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM ASSESSMENT
# ---------------------------------------------------------------------------
def test_build_mechanism_assessment():
    extraction_result = (
        make_z_scheme_extraction_result()
    )

    assessment = (
        build_mechanism_assessment(
            extraction_result=(
                extraction_result
            ),
            mechanism_assessment_id=(
                "MEA-0001"
            ),
            sample_id="SMP-0001",
            applies_to_series_id=(
                "SER-0001"
            ),
        )
    )

    assert (
        assessment.mechanism_assessment_id
        == "MEA-0001"
    )

    assert (
        assessment.sample_id
        == "SMP-0001"
    )

    assert (
        assessment.applies_to_series_id
        == "SER-0001"
    )

    assert (
        assessment.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        assessment.mechanism_reported
        == "Z-scheme"
    )

    assert (
        assessment.charge_transfer_class
        is None
    )

    assert (
        assessment.claim_explicit
        is True
    )

    assert (
        assessment.assessment_confidence
        is None
    )

    assert (
        assessment.manual_review_status
        == ManualReviewStatus.PENDING
    )

    assert (
        assessment.label_status
        == LabelStatus.PENDING_REVIEW
    )


# ---------------------------------------------------------------------------
# NO AUTOMATIC ML CLASS
# ---------------------------------------------------------------------------
def test_z_scheme_does_not_assign_ml_class():
    assessment = (
        build_mechanism_assessment(
            extraction_result=(
                make_z_scheme_extraction_result()
            ),
            mechanism_assessment_id=(
                "MEA-0001"
            ),
            sample_id="SMP-0001",
        )
    )

    assert (
        assessment.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        assessment.charge_transfer_class
        is None
    )


# ---------------------------------------------------------------------------
# BUILD UNKNOWN MECHANISM ASSESSMENT
# ---------------------------------------------------------------------------
def test_build_unknown_mechanism_assessment():
    extraction_result = (
        MechanismExtractionResult(
            mechanism_claims=[],
            characterization_candidates=[],
            mechanism_evidence_candidates=[],
        )
    )

    assessment = (
        build_mechanism_assessment(
            extraction_result=(
                extraction_result
            ),
            mechanism_assessment_id=(
                "MEA-0001"
            ),
            sample_id="SMP-0001",
        )
    )

    assert (
        assessment.mechanism_normalized
        == MechanismLabel.UNKNOWN
    )

    assert (
        assessment.mechanism_reported
        is None
    )

    assert (
        assessment.claim_explicit
        is False
    )

    assert (
        assessment.charge_transfer_class
        is None
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def test_build_mechanism_evidence():
    candidate = (
        make_z_scheme_extraction_result()
        .mechanism_evidence_candidates[
            0
        ]
    )

    evidence = (
        build_mechanism_evidence(
            candidate=candidate,
            evidence_id="EVD-0001",
            mechanism_assessment_id=(
                "MEA-0001"
            ),
        )
    )

    assert (
        evidence.evidence_id
        == "EVD-0001"
    )

    assert (
        evidence.mechanism_assessment_id
        == "MEA-0001"
    )

    assert (
        evidence.characterization_role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert (
        evidence.mechanism_discriminating
        is True
    )

    assert (
        evidence.requires_context
        is True
    )

    assert (
        EvidenceContextType.BAND_EDGES
        in evidence.required_context
    )

    assert (
        EvidenceContextType.REDOX_POTENTIALS
        in evidence.required_context
    )

    assert (
        evidence.support
        == EvidenceSupport.UNKNOWN
    )

    assert (
        evidence.evidence_strength
        == EvidenceStrength.UNKNOWN
    )

    assert (
        evidence.page_number
        == 9
    )

    assert (
        evidence.section_role
        == PaperSectionRole.MECHANISM
    )

    assert (
        evidence.reported_result
        == candidate.source_text
    )


# ---------------------------------------------------------------------------
# BUILD COMPLETE MECHANISM RECORDS
# ---------------------------------------------------------------------------
def test_build_mechanism_records():
    result = build_mechanism_records(
        extraction_result=(
            make_z_scheme_extraction_result()
        ),
        mechanism_assessment_id=(
            "MEA-0001"
        ),
        evidence_ids=[
            "EVD-0001",
            "EVD-0002",
        ],
        sample_id="SMP-0001",
        applies_to_series_id=(
            "SER-0001"
        ),
    )

    assert (
        result.mechanism_assessment
        .mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        result.mechanism_assessment
        .charge_transfer_class
        is None
    )

    assert (
        len(
            result.mechanism_evidence
        )
        == 2
    )

    assert (
        result.mechanism_evidence[
            0
        ].mechanism_assessment_id
        == "MEA-0001"
    )

    assert (
        result.mechanism_evidence[
            1
        ].mechanism_assessment_id
        == "MEA-0001"
    )


# ---------------------------------------------------------------------------
# EVIDENCE ID COUNT MUST MATCH
# ---------------------------------------------------------------------------
def test_evidence_id_count_must_match():
    with pytest.raises(
        ValueError,
        match=(
            "number of evidence IDs"
        ),
    ):
        build_mechanism_records(
            extraction_result=(
                make_z_scheme_extraction_result()
            ),
            mechanism_assessment_id=(
                "MEA-0001"
            ),
            evidence_ids=[
                "EVD-0001",
            ],
            sample_id="SMP-0001",
        )

