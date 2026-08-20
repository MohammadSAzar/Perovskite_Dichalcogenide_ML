import re

from pydantic import BaseModel

from psk_tmd.common.constants import (
    PaperSectionRole,
)
from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.consistency import (
    MechanismConsistencyResult,
    check_mechanism_consistency,
)
from psk_tmd.corpus.context import (
    build_evidence_context_window,
)
from psk_tmd.corpus.document import (
    DocumentTextResult,
)
from psk_tmd.corpus.extraction import (
    MechanismEvidenceCandidate,
    MechanismExtractionResult,
)
from psk_tmd.corpus.sections import (
    SectionedTextBlock,
    assign_pdf_block_sections,
)


# ---------------------------------------------------------------------------
# MECHANISM POSTPROCESS RESULT
# ---------------------------------------------------------------------------
class MechanismPostprocessResult(BaseModel):
    extraction_result: MechanismExtractionResult

    consistency_result: (
        MechanismConsistencyResult
        | None
    ) = None


# ---------------------------------------------------------------------------
# TOKENIZE TEXT
# ---------------------------------------------------------------------------
def tokenize_text(
    text: str,
) -> set[str]:
    return {
        token.lower()
        for token in re.findall(
            r"[A-Za-z0-9]+",
            normalize_whitespace(
                text
            ),
        )
        if len(token) >= 3
    }


# ---------------------------------------------------------------------------
# CALCULATE TEXT OVERLAP
# ---------------------------------------------------------------------------
def calculate_text_overlap(
    first_text: str,
    second_text: str,
) -> float:
    first_tokens = tokenize_text(
        first_text
    )

    second_tokens = tokenize_text(
        second_text
    )

    if (
        not first_tokens
        or not second_tokens
    ):
        return 0.0

    intersection = (
        first_tokens
        & second_tokens
    )

    smaller_size = min(
        len(first_tokens),
        len(second_tokens),
    )

    if smaller_size == 0:
        return 0.0

    return (
        len(intersection)
        / smaller_size
    )


# ---------------------------------------------------------------------------
# FIND EVIDENCE ANCHOR BLOCK
# ---------------------------------------------------------------------------
def find_evidence_anchor_block(
    document: DocumentTextResult,
    candidate: MechanismEvidenceCandidate,
) -> SectionedTextBlock | None:
    sectioned_blocks = (
        assign_pdf_block_sections(
            document
        )
    )

    candidate_text = (
        normalize_whitespace(
            candidate.source_text
        )
    )

    best_block: (
        SectionedTextBlock
        | None
    ) = None

    best_score = 0.0

    for block in sectioned_blocks:
        if (
            candidate.page_number
            is not None
            and block.page_number
            != candidate.page_number
        ):
            continue

        if (
            candidate.section_role
            != PaperSectionRole.OTHER
            and block.section_role
            != candidate.section_role
        ):
            continue

        if (
            candidate.section_title
            and block.section_title
            and block.section_title
            != candidate.section_title
        ):
            continue

        block_text = (
            normalize_whitespace(
                block.text
            )
        )

        if not block_text:
            continue

        if (
            candidate_text
            == block_text
        ):
            return block

        if (
            candidate_text
            in block_text
            or block_text
            in candidate_text
        ):
            score = 1.0

        else:
            score = (
                calculate_text_overlap(
                    candidate_text,
                    block_text,
                )
            )

        if score > best_score:
            best_score = score
            best_block = block

    if best_score < 0.35:
        return None

    return best_block


# ---------------------------------------------------------------------------
# GET EVIDENCE CONTEXT SIZE
# ---------------------------------------------------------------------------
def get_evidence_context_size(
    evidence_type: str,
) -> tuple[int, int]:
    context_sizes: dict[
        str,
        tuple[int, int],
    ] = {
        "xps": (
            0,
            1,
        ),
        "esr": (
            0,
            3,
        ),
        "radical_trapping": (
            0,
            3,
        ),
        "band_alignment": (
            0,
            2,
        ),
        "work_function": (
            0,
            2,
        ),
        "kelvin_probe": (
            0,
            2,
        ),
        "photodeposition": (
            0,
            2,
        ),
    }

    return context_sizes.get(
        evidence_type,
        (
            0,
            2,
        ),
    )


# ---------------------------------------------------------------------------
# COMPLETE EVIDENCE CANDIDATE
# ---------------------------------------------------------------------------
def complete_evidence_candidate(
    document: DocumentTextResult,
    candidate: MechanismEvidenceCandidate,
    previous_blocks: int | None = None,
    next_blocks: int | None = None,
) -> MechanismEvidenceCandidate:
    anchor = find_evidence_anchor_block(
        document=document,
        candidate=candidate,
    )

    if anchor is None:
        return candidate

    (
        default_previous_blocks,
        default_next_blocks,
    ) = get_evidence_context_size(
        candidate.evidence_type
    )

    if previous_blocks is None:
        previous_blocks = (
            default_previous_blocks
        )

    if next_blocks is None:
        next_blocks = (
            default_next_blocks
        )

    context_window = (
        build_evidence_context_window(
            document=document,
            page_number=(
                anchor.page_number
            ),
            block_index=(
                anchor.block_index
            ),
            previous_blocks=(
                previous_blocks
            ),
            next_blocks=(
                next_blocks
            ),
        )
    )

    if context_window is None:
        return candidate

    return candidate.model_copy(
        update={
            "source_text": (
                context_window.text
            ),
        }
    )


# ---------------------------------------------------------------------------
# COMPLETE MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def complete_mechanism_evidence(
    document: DocumentTextResult,
    extraction_result: MechanismExtractionResult,
    previous_blocks: int | None = None,
    next_blocks: int | None = None,
) -> MechanismExtractionResult:
    completed_candidates = [
        complete_evidence_candidate(
            document=document,
            candidate=candidate,
            previous_blocks=(
                previous_blocks
            ),
            next_blocks=(
                next_blocks
            ),
        )
        for candidate
        in (
            extraction_result
            .mechanism_evidence_candidates
        )
    ]

    return extraction_result.model_copy(
        update={
            "mechanism_evidence_candidates": (
                completed_candidates
            ),
        }
    )


# ---------------------------------------------------------------------------
# CARRIER-PATH TEXT
# ---------------------------------------------------------------------------
def contains_carrier_path_terms(
    text: str,
) -> bool:
    clean_text = (
        normalize_whitespace(
            text
        ).lower()
    )

    marker_groups = (
        (
            "electron",
            "electrons",
        ),
        (
            "hole",
            "holes",
        ),
        (
            "conduction band",
            "cb",
        ),
        (
            "valence band",
            "vb",
        ),
        (
            "transfer",
            "move",
            "migrate",
            "recombine",
            "recombination",
        ),
    )

    matched_groups = 0

    for group in marker_groups:
        if any(
            marker in clean_text
            for marker in group
        ):
            matched_groups += 1

    return matched_groups >= 3


# ---------------------------------------------------------------------------
# BUILD CONSISTENCY SOURCE TEXT
# ---------------------------------------------------------------------------
def build_consistency_source_text(
    extraction_result: MechanismExtractionResult,
) -> str | None:
    carrier_texts = [
        candidate.source_text
        for candidate
        in (
            extraction_result
            .mechanism_evidence_candidates
        )
        if contains_carrier_path_terms(
            candidate.source_text
        )
    ]

    if carrier_texts:
        return normalize_whitespace(
            " ".join(
                carrier_texts
            )
        )

    if (
        extraction_result
        .mechanism_claims
    ):
        claim = (
            extraction_result
            .mechanism_claims[
                0
            ]
        )

        if contains_carrier_path_terms(
            claim.source_text
        ):
            return normalize_whitespace(
                claim.source_text
            )

    return None


# ---------------------------------------------------------------------------
# POSTPROCESS MECHANISM EXTRACTION
# ---------------------------------------------------------------------------
def postprocess_mechanism_extraction(
    document: DocumentTextResult,
    extraction_result: MechanismExtractionResult,
) -> MechanismPostprocessResult:
    completed_result = (
        complete_mechanism_evidence(
            document=document,
            extraction_result=(
                extraction_result
            ),
        )
    )

    if not (
        completed_result
        .mechanism_claims
    ):
        return MechanismPostprocessResult(
            extraction_result=(
                completed_result
            ),
            consistency_result=None,
        )

    source_text = (
        build_consistency_source_text(
            completed_result
        )
    )

    if source_text is None:
        return MechanismPostprocessResult(
            extraction_result=(
                completed_result
            ),
            consistency_result=None,
        )

    reported_mechanism = (
        completed_result
        .mechanism_claims[
            0
        ]
        .mechanism_normalized
    )

    consistency_result = (
        check_mechanism_consistency(
            reported_mechanism=(
                reported_mechanism
            ),
            source_text=source_text,
        )
    )

    return MechanismPostprocessResult(
        extraction_result=(
            completed_result
        ),
        consistency_result=(
            consistency_result
        ),
    )

