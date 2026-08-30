from collections.abc import Iterable

from psk_tmd.common.constants import (
    BandClaimContext,
    BandGapType,
    BandReferenceScale,
    ManualReviewStatus,
    MaterialType,
)
from psk_tmd.common.models import (
    MaterialBandRecord,
    PairRecord,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_structured_extraction import (
    StructuredBandValue,
)


# ---------------------------------------------------------------------------
# GET MATERIAL FORMULAS
# ---------------------------------------------------------------------------
def get_material_formulas(
    pair: PairRecord,
    *,
    material_type: MaterialType,
) -> tuple[
    str,
    str | None,
]:
    if material_type == MaterialType.PSK:
        return (
            pair.psk_formula_reported,
            pair.psk_formula_normalized,
        )

    if material_type == MaterialType.TMD:
        return (
            pair.tmd_formula_reported,
            pair.tmd_formula_normalized,
        )

    raise ValueError(
        f"Unsupported material type: "
        f"{material_type}"
    )


# ---------------------------------------------------------------------------
# FILTER MATERIAL VALUES
# ---------------------------------------------------------------------------
def filter_material_values(
    values: Iterable[
        StructuredBandValue
    ],
    *,
    material_type: MaterialType,
) -> list[
    StructuredBandValue
]:
    return [
        value
        for value in values
        if value.material_type
        == material_type
    ]


# ---------------------------------------------------------------------------
# FILTER PROPERTY VALUES
# ---------------------------------------------------------------------------
def filter_property_values(
    values: Iterable[
        StructuredBandValue
    ],
    *,
    property_type: BandPropertyType,
) -> list[
    StructuredBandValue
]:
    return [
        value
        for value in values
        if value.property_type
        == property_type
    ]


# ---------------------------------------------------------------------------
# RESOLVE UNIQUE PROPERTY CLAIM
# ---------------------------------------------------------------------------
def resolve_unique_property_claim(
    values: Iterable[
        StructuredBandValue
    ],
    *,
    property_type: BandPropertyType,
) -> StructuredBandValue | None:
    candidates = (
        filter_property_values(
            values,
            property_type=property_type,
        )
    )

    if not candidates:
        return None

    unique_numeric_values = {
        round(
            candidate.numeric_value,
            8,
        )
        for candidate in candidates
    }

    if len(
        unique_numeric_values
    ) > 1:
        raise ValueError(
            "Conflicting values found for "
            f"{property_type.value}: "
            f"{sorted(unique_numeric_values)}"
        )

    return candidates[
        0
    ]


# ---------------------------------------------------------------------------
# RESOLVE BAND GAP TYPE
# ---------------------------------------------------------------------------
def resolve_band_gap_type(
    band_gap_claim: StructuredBandValue | None,
) -> BandGapType:
    if (
        band_gap_claim is None
        or band_gap_claim.band_gap_type
        is None
    ):
        return BandGapType.UNKNOWN

    return (
        band_gap_claim.band_gap_type
    )


# ---------------------------------------------------------------------------
# RESOLVE CLAIM CONTEXT
# ---------------------------------------------------------------------------
def resolve_record_claim_context(
    claims: Iterable[
        StructuredBandValue | None
    ],
) -> BandClaimContext:
    contexts = {
        claim.claim_context
        for claim in claims
        if claim is not None
    }

    if not contexts:
        return (
            BandClaimContext.AMBIGUOUS
        )

    if len(
        contexts
    ) == 1:
        return next(
            iter(
                contexts
            )
        )

    return (
        BandClaimContext.AMBIGUOUS
    )


# ---------------------------------------------------------------------------
# RESOLVE REFERENCE SCALE
# ---------------------------------------------------------------------------
def resolve_record_reference_scale(
    claims: Iterable[
        StructuredBandValue | None
    ],
) -> BandReferenceScale:
    scales = {
        claim.reference_scale
        for claim in claims
        if (
            claim is not None
            and claim.reference_scale
            is not None
        )
    }

    if not scales:
        return (
            BandReferenceScale.UNKNOWN
        )

    if len(
        scales
    ) == 1:
        return next(
            iter(
                scales
            )
        )

    return (
        BandReferenceScale.UNKNOWN
    )


# ---------------------------------------------------------------------------
# BUILD SOURCE TEXT
# ---------------------------------------------------------------------------
def build_source_text(
    claims: Iterable[
        StructuredBandValue | None
    ],
) -> str | None:
    source_texts: list[
        str
    ] = []

    for claim in claims:
        if claim is None:
            continue

        text = claim.source_text.strip()

        if (
            text
            and text
            not in source_texts
        ):
            source_texts.append(
                text
            )

    if not source_texts:
        return None

    return "\n\n".join(
        source_texts
    )


# ---------------------------------------------------------------------------
# BUILD MATERIAL BAND RECORD
# ---------------------------------------------------------------------------
def build_material_band_record(
    *,
    band_record_id: str,
    paper_id: str,
    pair: PairRecord,
    material_type: MaterialType,
    values: Iterable[
        StructuredBandValue
    ],
    source_location: str | None = None,
    band_gap_method: str | None = None,
    reported_reference_detail: str | None = None,
    notes: str | None = None,
    manual_review_status: ManualReviewStatus = (
        ManualReviewStatus.PENDING
    ),
) -> MaterialBandRecord:
    material_values = (
        filter_material_values(
            values,
            material_type=material_type,
        )
    )

    band_gap_claim = (
        resolve_unique_property_claim(
            material_values,
            property_type=(
                BandPropertyType.BAND_GAP
            ),
        )
    )

    cbm_claim = (
        resolve_unique_property_claim(
            material_values,
            property_type=(
                BandPropertyType.CBM
            ),
        )
    )

    vbm_claim = (
        resolve_unique_property_claim(
            material_values,
            property_type=(
                BandPropertyType.VBM
            ),
        )
    )

    formula_reported, formula_normalized = (
        get_material_formulas(
            pair,
            material_type=material_type,
        )
    )

    selected_claims = [
        band_gap_claim,
        cbm_claim,
        vbm_claim,
    ]

    return MaterialBandRecord(
        band_record_id=band_record_id,
        paper_id=paper_id,
        pair_id=pair.pair_id,
        material_type=material_type,
        formula_reported=(
            formula_reported
        ),
        formula_normalized=(
            formula_normalized
        ),
        reported_band_gap_ev=(
            None
            if band_gap_claim is None
            else band_gap_claim.numeric_value
        ),
        band_gap_type=(
            resolve_band_gap_type(
                band_gap_claim
            )
        ),
        band_gap_method=(
            band_gap_method
        ),
        reported_cbm=(
            None
            if cbm_claim is None
            else cbm_claim.numeric_value
        ),
        reported_vbm=(
            None
            if vbm_claim is None
            else vbm_claim.numeric_value
        ),
        reported_reference_scale=(
            resolve_record_reference_scale(
                [
                    cbm_claim,
                    vbm_claim,
                ]
            )
        ),
        reported_reference_detail=(
            reported_reference_detail
        ),
        claim_context=(
            resolve_record_claim_context(
                selected_claims
            )
        ),
        source_location=(
            source_location
        ),
        source_text=(
            build_source_text(
                selected_claims
            )
        ),
        manual_review_status=(
            manual_review_status
        ),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# BUILD PAIR MATERIAL BAND RECORDS
# ---------------------------------------------------------------------------
def build_pair_material_band_records(
    *,
    paper_id: str,
    pair: PairRecord,
    values: Iterable[
        StructuredBandValue
    ],
    psk_band_record_id: str,
    tmd_band_record_id: str,
    source_location: str | None = None,
) -> list[
    MaterialBandRecord
]:
    value_list = list(
        values
    )

    psk_record = (
        build_material_band_record(
            band_record_id=(
                psk_band_record_id
            ),
            paper_id=paper_id,
            pair=pair,
            material_type=(
                MaterialType.PSK
            ),
            values=value_list,
            source_location=(
                source_location
            ),
        )
    )

    tmd_record = (
        build_material_band_record(
            band_record_id=(
                tmd_band_record_id
            ),
            paper_id=paper_id,
            pair=pair,
            material_type=(
                MaterialType.TMD
            ),
            values=value_list,
            source_location=(
                source_location
            ),
        )
    )

    return [
        psk_record,
        tmd_record,
    ]

