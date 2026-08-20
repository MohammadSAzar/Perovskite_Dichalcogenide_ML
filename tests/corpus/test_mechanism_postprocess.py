from psk_tmd.common.constants import (
    CharacterizationRole,
    EvidenceContextType,
    MechanismLabel,
    PaperSectionRole,
)
from psk_tmd.corpus.consistency import (
    CarrierPathwayType,
    MechanismConsistencyStatus,
)
from psk_tmd.corpus.document import (
    DocumentBlock,
    DocumentPage,
    DocumentTextResult,
)
from psk_tmd.corpus.extraction import (
    MechanismClaimCandidate,
    MechanismEvidenceCandidate,
    MechanismExtractionResult,
)
from psk_tmd.corpus.mechanism_postprocess import (
    build_consistency_source_text,
    calculate_text_overlap,
    complete_evidence_candidate,
    complete_mechanism_evidence,
    find_evidence_anchor_block,
    get_evidence_context_size,
    postprocess_mechanism_extraction,
)


# ---------------------------------------------------------------------------
# MAKE POSTPROCESS DOCUMENT
# ---------------------------------------------------------------------------
def make_postprocess_document(
) -> DocumentTextResult:
    return DocumentTextResult(
        pages=[
            DocumentPage(
                page_number=9,
                text="",
                blocks=[
                    DocumentBlock(
                        block_index=1,
                        text=(
                            "3.5. Possible "
                            "photocatalytic mechanism"
                        ),
                    ),
                    DocumentBlock(
                        block_index=2,
                        text=(
                            "Active species trapping "
                            "experiments were performed "
                            "using BQ, TEOA and t-BuOH."
                        ),
                    ),
                    DocumentBlock(
                        block_index=3,
                        text=(
                            "Addition of BQ strongly "
                            "suppressed the degradation "
                            "reaction."
                        ),
                    ),
                    DocumentBlock(
                        block_index=4,
                        text=(
                            "The result indicates that "
                            "superoxide radicals are "
                            "important active species."
                        ),
                    ),
                    DocumentBlock(
                        block_index=5,
                        text=(
                            "3.6. Photocatalytic "
                            "mechanism"
                        ),
                    ),
                    DocumentBlock(
                        block_index=6,
                        text=(
                            "Electrons in the conduction "
                            "band of WS2 transfer to the "
                            "conduction band of CaTiO3, "
                            "while holes move from the "
                            "valence band of CaTiO3 to "
                            "the valence band of WS2."
                        ),
                    ),
                ],
            ),
        ],
        sections=[],
        full_text="",
        page_count=1,
        source_format="pdf",
        extraction_method=(
            "pymupdf_blocks"
        ),
    )


# ---------------------------------------------------------------------------
# MAKE POSTPROCESS EXTRACTION RESULT
# ---------------------------------------------------------------------------
def make_postprocess_extraction_result(
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
                    CharacterizationRole
                    .MECHANISM_ASSESSMENT
                ),
                mechanism_discriminating=True,
                requires_context=True,
                required_context=[
                    EvidenceContextType
                    .BAND_EDGES,
                    EvidenceContextType
                    .REDOX_POTENTIALS,
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
                    "trapping experiments",
                ],
                source_text=(
                    "Active species trapping "
                    "experiments were performed "
                    "using BQ, TEOA and t-BuOH."
                ),
                score=20.0,
            ),
            MechanismEvidenceCandidate(
                evidence_type=(
                    "band_alignment"
                ),
                characterization_role=(
                    CharacterizationRole
                    .BAND_STRUCTURE
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
                    "Electrons in the conduction "
                    "band of WS2 transfer to the "
                    "conduction band of CaTiO3, "
                    "while holes move from the "
                    "valence band of CaTiO3 to "
                    "the valence band of WS2."
                ),
                score=10.0,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# TEXT OVERLAP
# ---------------------------------------------------------------------------
def test_calculate_text_overlap():
    score = calculate_text_overlap(
        (
            "Active species trapping "
            "experiments were performed."
        ),
        (
            "Active species trapping "
            "experiments were performed "
            "using several scavengers."
        ),
    )

    assert score > 0.8


# ---------------------------------------------------------------------------
# FIND EVIDENCE ANCHOR
# ---------------------------------------------------------------------------
def test_find_evidence_anchor_block():
    candidate = (
        make_postprocess_extraction_result()
        .mechanism_evidence_candidates[
            0
        ]
    )

    block = find_evidence_anchor_block(
        document=(
            make_postprocess_document()
        ),
        candidate=candidate,
    )

    assert block is not None

    assert (
        block.block_index
        == 2
    )


# ---------------------------------------------------------------------------
# EVIDENCE-SPECIFIC CONTEXT SIZES
# ---------------------------------------------------------------------------
def test_evidence_context_sizes():
    assert (
        get_evidence_context_size(
            "xps"
        )
        == (
            0,
            1,
        )
    )

    assert (
        get_evidence_context_size(
            "radical_trapping"
        )
        == (
            0,
            3,
        )
    )

    assert (
        get_evidence_context_size(
            "esr"
        )
        == (
            0,
            3,
        )
    )


# ---------------------------------------------------------------------------
# COMPLETE SINGLE EVIDENCE CANDIDATE
# ---------------------------------------------------------------------------
def test_complete_single_evidence_candidate():
    candidate = (
        make_postprocess_extraction_result()
        .mechanism_evidence_candidates[
            0
        ]
    )

    result = (
        complete_evidence_candidate(
            document=(
                make_postprocess_document()
            ),
            candidate=candidate,
        )
    )

    assert (
        "using BQ"
        in result.source_text
    )

    assert (
        "strongly suppressed"
        in result.source_text
    )

    assert (
        "superoxide radicals"
        in result.source_text
    )


# ---------------------------------------------------------------------------
# COMPLETE MECHANISM EVIDENCE EXISTS
# ---------------------------------------------------------------------------
def test_complete_mechanism_evidence_exists():
    result = (
        complete_mechanism_evidence(
            document=(
                make_postprocess_document()
            ),
            extraction_result=(
                make_postprocess_extraction_result()
            ),
        )
    )

    assert (
        len(
            result
            .mechanism_evidence_candidates
        )
        == 2
    )


# ---------------------------------------------------------------------------
# COMPLETE RADICAL-TRAPPING RESULT
# ---------------------------------------------------------------------------
def test_complete_radical_trapping_result():
    result = (
        complete_mechanism_evidence(
            document=(
                make_postprocess_document()
            ),
            extraction_result=(
                make_postprocess_extraction_result()
            ),
            next_blocks=2,
        )
    )

    radical = (
        result
        .mechanism_evidence_candidates[
            0
        ]
    )

    assert (
        "using BQ"
        in radical.source_text
    )

    assert (
        "strongly suppressed"
        in radical.source_text
    )

    assert (
        "superoxide radicals"
        in radical.source_text
    )


# ---------------------------------------------------------------------------
# BUILD CARRIER-PATH SOURCE TEXT
# ---------------------------------------------------------------------------
def test_build_consistency_source_text():
    text = (
        build_consistency_source_text(
            make_postprocess_extraction_result()
        )
    )

    assert text is not None

    assert (
        "conduction band"
        in text
    )

    assert (
        "valence band"
        in text
    )


# ---------------------------------------------------------------------------
# DETECT POTENTIAL Z-SCHEME INCONSISTENCY
# ---------------------------------------------------------------------------
def test_postprocess_detects_potential_inconsistency():
    result = (
        postprocess_mechanism_extraction(
            document=(
                make_postprocess_document()
            ),
            extraction_result=(
                make_postprocess_extraction_result()
            ),
        )
    )

    assert (
        result.consistency_result
        is not None
    )

    assert (
        result.consistency_result
        .pathway_type
        == (
            CarrierPathwayType
            .TYPE_II_LIKE
        )
    )

    assert (
        result.consistency_result
        .consistency_status
        == (
            MechanismConsistencyStatus
            .POTENTIALLY_INCONSISTENT
        )
    )


# ---------------------------------------------------------------------------
# PRESERVE REPORTED MECHANISM
# ---------------------------------------------------------------------------
def test_postprocess_does_not_relabel_mechanism():
    result = (
        postprocess_mechanism_extraction(
            document=(
                make_postprocess_document()
            ),
            extraction_result=(
                make_postprocess_extraction_result()
            ),
        )
    )

    claim = (
        result.extraction_result
        .mechanism_claims[
            0
        ]
    )

    assert (
        claim.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        claim.charge_transfer_class
        is None
    )


