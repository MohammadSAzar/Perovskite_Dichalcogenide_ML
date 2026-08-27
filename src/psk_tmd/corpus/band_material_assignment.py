import re

from dataclasses import dataclass

from psk_tmd.common.constants import (
    MaterialType,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_claims import (
    BandClaimCandidate,
)


# ---------------------------------------------------------------------------
# BAND CLAIM MATERIAL ASSIGNMENT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class BandClaimMaterialAssignment:
    claim: BandClaimCandidate
    material_type: MaterialType | None
    formula: str | None
    assignment_basis: str | None


# ---------------------------------------------------------------------------
# UNICODE SUBSCRIPT TRANSLATION
# ---------------------------------------------------------------------------
SUBSCRIPT_TRANSLATION = str.maketrans(
    {
        "₀": "0",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "₄": "4",
        "₅": "5",
        "₆": "6",
        "₇": "7",
        "₈": "8",
        "₉": "9",
        "₋": "-",
        "₊": "+",
    }
)


# ---------------------------------------------------------------------------
# NORMALIZE FORMULA TEXT
# ---------------------------------------------------------------------------
def normalize_formula_text(
    text: str,
) -> str:
    return (
        text
        .translate(
            SUBSCRIPT_TRANSLATION
        )
        .replace(
            " ",
            "",
        )
    )


# ---------------------------------------------------------------------------
# NORMALIZE SEARCH TEXT
# ---------------------------------------------------------------------------
def normalize_search_text(
    text: str,
) -> str:
    return text.translate(
        SUBSCRIPT_TRANSLATION
    )


# ---------------------------------------------------------------------------
# FORMULA OCCURS IN TEXT
# ---------------------------------------------------------------------------
def formula_occurs_in_text(
    text: str,
    formula: str,
) -> bool:
    normalized_text = (
        normalize_search_text(
            text
        )
    )

    normalized_formula = (
        normalize_formula_text(
            formula
        )
    )

    if not normalized_formula:
        return False

    pattern = re.compile(
        rf"(?<![A-Za-z0-9])"
        rf"{re.escape(normalized_formula)}"
        rf"(?![A-Za-z0-9])"
    )

    return (
        pattern.search(
            normalized_text
        )
        is not None
    )

# ---------------------------------------------------------------------------
# BUILD MATERIAL FORMULA VARIANTS
# ---------------------------------------------------------------------------
def build_formula_variants(
    *,
    formula_reported: str,
    formula_normalized: str | None,
) -> set[
    str
]:
    variants = {
        normalize_formula_text(
            formula_reported
        )
    }

    if formula_normalized:
        variants.add(
            normalize_formula_text(
                formula_normalized
            )
        )

    return {
        variant
        for variant in variants
        if variant
    }


# ---------------------------------------------------------------------------
# MATERIAL IS MENTIONED
# ---------------------------------------------------------------------------
def material_is_mentioned(
    text: str,
    *,
    formula_reported: str,
    formula_normalized: str | None,
) -> bool:
    variants = (
        build_formula_variants(
            formula_reported=(
                formula_reported
            ),
            formula_normalized=(
                formula_normalized
            ),
        )
    )

    return any(
        formula_occurs_in_text(
            text,
            formula,
        )
        for formula in variants
    )


# ---------------------------------------------------------------------------
# ASSIGN BAND CLAIM TO MATERIAL
# ---------------------------------------------------------------------------
def assign_band_claim_to_material(
    claim: BandClaimCandidate,
    *,
    pair: PairRecord,
) -> BandClaimMaterialAssignment:
    psk_mentioned = (
        material_is_mentioned(
            claim.source_text,
            formula_reported=(
                pair
                .psk_formula_reported
            ),
            formula_normalized=(
                pair
                .psk_formula_normalized
            ),
        )
    )

    tmd_mentioned = (
        material_is_mentioned(
            claim.source_text,
            formula_reported=(
                pair
                .tmd_formula_reported
            ),
            formula_normalized=(
                pair
                .tmd_formula_normalized
            ),
        )
    )

    if (
        psk_mentioned
        and not tmd_mentioned
    ):
        return (
            BandClaimMaterialAssignment(
                claim=claim,
                material_type=(
                    MaterialType.PSK
                ),
                formula=(
                    pair
                    .psk_formula_normalized
                    or pair
                    .psk_formula_reported
                ),
                assignment_basis=(
                    "PSK formula explicitly "
                    "mentioned in claim sentence."
                ),
            )
        )

    if (
        tmd_mentioned
        and not psk_mentioned
    ):
        return (
            BandClaimMaterialAssignment(
                claim=claim,
                material_type=(
                    MaterialType.TMD
                ),
                formula=(
                    pair
                    .tmd_formula_normalized
                    or pair
                    .tmd_formula_reported
                ),
                assignment_basis=(
                    "TMD formula explicitly "
                    "mentioned in claim sentence."
                ),
            )
        )

    if (
        psk_mentioned
        and tmd_mentioned
    ):
        return (
            BandClaimMaterialAssignment(
                claim=claim,
                material_type=None,
                formula=None,
                assignment_basis=(
                    "Both pair materials are "
                    "mentioned in claim sentence."
                ),
            )
        )

    return (
        BandClaimMaterialAssignment(
            claim=claim,
            material_type=None,
            formula=None,
            assignment_basis=(
                "No pair material formula is "
                "explicitly mentioned in claim "
                "sentence."
            ),
        )
    )


# ---------------------------------------------------------------------------
# ASSIGN BAND CLAIMS TO MATERIALS
# ---------------------------------------------------------------------------
def assign_band_claims_to_materials(
    claims: list[
        BandClaimCandidate
    ],
    *,
    pair: PairRecord,
) -> list[
    BandClaimMaterialAssignment
]:
    return [
        assign_band_claim_to_material(
            claim,
            pair=pair,
        )
        for claim in claims
    ]

