import re

from dataclasses import dataclass

from psk_tmd.common.constants import (
    BandClaimContext,
    BandGapType,
    BandReferenceScale,
    MaterialType,
)
from psk_tmd.common.models import (
    PairRecord,
)
from psk_tmd.corpus.band_candidates import (
    BandPropertyType,
)
from psk_tmd.corpus.band_claim_context import (
    classify_band_claim_context,
)
from psk_tmd.corpus.band_material_assignment import (
    formula_occurs_in_text,
)


# ---------------------------------------------------------------------------
# STRUCTURED BAND VALUE
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class StructuredBandValue:
    property_type: BandPropertyType
    material_type: MaterialType
    formula: str
    numeric_value: float
    claim_context: BandClaimContext
    reference_scale: BandReferenceScale | None
    band_gap_type: BandGapType | None
    source_text: str
    extraction_basis: str


# ---------------------------------------------------------------------------
# INTERNAL SUBJECT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SubjectEntry:
    material_type: MaterialType | None
    formula: str | None
    is_heterostructure: bool = False


# ---------------------------------------------------------------------------
# NUMERIC PATTERN
# ---------------------------------------------------------------------------
NUMERIC_PATTERN = (
    r"[-+]?"
    r"(?:\d+(?:\.\d+)?|\.\d+)"
)


# ---------------------------------------------------------------------------
# BAND GAP LIST PATTERN
# ---------------------------------------------------------------------------
BAND_GAP_LIST_PATTERN = re.compile(
    rf"(?:"
    rf"band\s*gap\s+energies"
    rf"|bandgap\s+energies"
    rf"|E\s*_?\s*g"
    rf")"
    rf"\s+(?:of\s+)?"
    rf"(?P<subjects>.+?)"
    rf"\s+(?:are|were)\s+"
    rf"(?:calculated|determined|given)"
    rf".*?"
    rf"(?:to\s+be|which\s+are)"
    rf"\s+"
    rf"(?P<values>.+?)"
    rf"\s*,?\s*respectively\b",
    flags=re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# CB LIST PATTERN
# ---------------------------------------------------------------------------
CB_LIST_PATTERN = re.compile(
    rf"(?:"
    rf"conduction\s+band"
    rf"(?:\s*\(CB\))?"
    rf"|CB"
    rf"|E\s*_?\s*CB"
    rf")"
    rf"\s+"
    rf"(?:"
    rf"potentials?"
    rf"|positions?"
    rf"|values?"
    rf"|energy\s+levels?"
    rf")"
    rf"\s+of\s+"
    rf"(?P<subjects>.+?)"
    rf"\s+(?:are|were)\s+"
    rf"(?:"
    rf"determined"
    rf"|calculated"
    rf"|estimated"
    rf")"
    rf".*?"
    rf"(?:to\s+be|they\s+are)"
    rf"\s+"
    rf"(?P<values>.+?)"
    rf"\s*,?\s*respectively\b",
    flags=re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# VB LIST PATTERN
# ---------------------------------------------------------------------------
VB_LIST_PATTERN = re.compile(
    rf"(?:"
    rf"valence(?:\s+|-)+band"
    rf"(?:\s*\(VB\))?"
    rf"|VB"
    rf"|E\s*_?\s*VB"
    rf")"
    rf"(?:\s*-\s*XPS)?"
    rf"\s+"
    rf"(?:"
    rf"potentials?"
    rf"|positions?"
    rf"|values?"
    rf"|energy\s+levels?"
    rf")"
    rf"\s+of\s+"
    rf"(?P<subjects>.+?)"
    rf"\s+(?:are|were)\s+"
    rf"(?:"
    rf"determined"
    rf"|calculated"
    rf"|estimated"
    rf"|measured"
    rf")"
    rf".*?"
    rf"(?:to\s+be|they\s+are)"
    rf"\s+"
    rf"(?P<values>.+?)"
    rf"\s*,?\s*respectively\b",
    flags=re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# NORMALIZE PDF NUMERIC TEXT
# ---------------------------------------------------------------------------
def normalize_pdf_numeric_text(
    text: str,
) -> str:
    normalized = text

    normalized = normalized.replace(
        "\u2212",
        "-",
    )

    normalized = normalized.replace(
        "ظêْ",
        "-",
    )

    normalized = normalized.replace(
        "\ufffe",
        "",
    )

    normalized = normalized.replace(
        "\u00ad",
        "",
    )

    normalized = re.sub(
        r"[–—]\s*(?=\d)",
        "-",
        normalized,
    )

    normalized = re.sub(
        r"([+-])\s+(?=\d)",
        r"\1",
        normalized,
    )

    normalized = re.sub(
        r"(?<=[A-Za-z])-\s+"
        r"(?=[A-Za-z])",
        "",
        normalized,
    )

    return normalized


# ---------------------------------------------------------------------------
# CLEAN SOURCE TEXT
# ---------------------------------------------------------------------------
def clean_source_text(
    text: str,
) -> str:
    return " ".join(
        text.split()
    )


# ---------------------------------------------------------------------------
# GET MATERIAL FORMULA
# ---------------------------------------------------------------------------
def get_material_formula(
    pair: PairRecord,
    material_type: MaterialType,
) -> str:
    if (
        material_type
        == MaterialType.PSK
    ):
        return (
            pair.psk_formula_normalized
            or pair.psk_formula_reported
        )

    return (
        pair.tmd_formula_normalized
        or pair.tmd_formula_reported
    )


# ---------------------------------------------------------------------------
# GET FORMULA MATERIAL TYPE
# ---------------------------------------------------------------------------
def get_formula_material_type(
    formula: str,
    *,
    pair: PairRecord,
) -> MaterialType | None:
    if formula_occurs_in_text(
        formula,
        pair.psk_formula_normalized
        or pair.psk_formula_reported,
    ):
        return MaterialType.PSK

    if formula_occurs_in_text(
        formula,
        pair.tmd_formula_normalized
        or pair.tmd_formula_reported,
    ):
        return MaterialType.TMD

    return None


# ---------------------------------------------------------------------------
# RESOLVE REFERENCE SCALE
# ---------------------------------------------------------------------------
def resolve_reference_scale(
    text: str,
) -> BandReferenceScale | None:
    if re.search(
        r"\b(?:vs\.?\s*)?NHE\b",
        text,
        flags=re.IGNORECASE,
    ):
        return BandReferenceScale.NHE

    if re.search(
        r"\b(?:vs\.?\s*)?SHE\b",
        text,
        flags=re.IGNORECASE,
    ):
        return BandReferenceScale.SHE

    if re.search(
        r"\b(?:vs\.?\s*)?RHE\b",
        text,
        flags=re.IGNORECASE,
    ):
        return BandReferenceScale.RHE

    if re.search(
        r"\bAg\s*/\s*AgCl\b",
        text,
        flags=re.IGNORECASE,
    ):
        return BandReferenceScale.AG_AGCL

    if re.search(
        r"\bSCE\b",
        text,
        flags=re.IGNORECASE,
    ):
        return BandReferenceScale.SCE

    return None


# ---------------------------------------------------------------------------
# RESOLVE CLAIM CONTEXT
# ---------------------------------------------------------------------------
def resolve_claim_context(
    text: str,
) -> BandClaimContext:
    result = (
        classify_band_claim_context(
            text
        )
    )

    if (
        result
        != BandClaimContext.AMBIGUOUS
    ):
        return result

    current_work_patterns = [
        r"\bfrom\s+fig\.?\s*\d+",
        r"\bgiven\s+in\s+fig\.?\s*\d+",
        r"\bshown\s+in\s+fig\.?\s*\d+",
        r"\bas\s+shown\s+in\s+fig\.?\s*\d+",
        r"\bobtained\s+from\s+fig\.?\s*\d+",
        r"\bare\s+calculated\s+to\s+be\b",
        r"\bare\s+determined\s+to\s+be\b",
        r"\bwere\s+calculated\s+to\s+be\b",
        r"\bwere\s+determined\s+to\s+be\b",
        r"\bcan\s+be\s+calculated\b",
        r"\bcan\s+be\s+determined\b",
        r"\bbased\s+on\s+the\s+above\b",
        r"\bit\s+is\s+concluded\b",
        r"\bwe\s+measured\b",
        r"\bin\s+this\s+study\b",
        r"\bin\s+this\s+work\b",
    ]

    if any(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
        is not None
        for pattern in current_work_patterns
    ):
        return (
            BandClaimContext.CURRENT_WORK
        )

    return (
        BandClaimContext.AMBIGUOUS
    )


# ---------------------------------------------------------------------------
# EXTRACT NUMERIC VALUES
# ---------------------------------------------------------------------------
def extract_numeric_values(
    text: str,
) -> list[
    float
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    return [
        float(
            match.group(
                0
            )
        )
        for match in re.finditer(
            NUMERIC_PATTERN,
            normalized,
        )
    ]


# ---------------------------------------------------------------------------
# SPLIT SUBJECT TEXT
# ---------------------------------------------------------------------------
def split_subject_text(
    text: str,
) -> list[
    str
]:
    parts = re.split(
        r"\s*,\s*|\s+\band\b\s+",
        text,
        flags=re.IGNORECASE,
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


# ---------------------------------------------------------------------------
# CLASSIFY SUBJECT
# ---------------------------------------------------------------------------
def classify_subject(
    text: str,
    *,
    pair: PairRecord,
) -> SubjectEntry:
    has_psk = (
        formula_occurs_in_text(
            text,
            pair.psk_formula_normalized
            or pair.psk_formula_reported,
        )
    )

    has_tmd = (
        formula_occurs_in_text(
            text,
            pair.tmd_formula_normalized
            or pair.tmd_formula_reported,
        )
    )

    if (
        has_psk
        and has_tmd
    ):
        return (
            SubjectEntry(
                material_type=None,
                formula=None,
                is_heterostructure=True,
            )
        )

    if has_psk:
        return (
            SubjectEntry(
                material_type=(
                    MaterialType.PSK
                ),
                formula=(
                    get_material_formula(
                        pair,
                        MaterialType.PSK,
                    )
                ),
            )
        )

    if has_tmd:
        return (
            SubjectEntry(
                material_type=(
                    MaterialType.TMD
                ),
                formula=(
                    get_material_formula(
                        pair,
                        MaterialType.TMD,
                    )
                ),
            )
        )

    return (
        SubjectEntry(
            material_type=None,
            formula=None,
        )
    )


# ---------------------------------------------------------------------------
# EXTRACT SUBJECTS
# ---------------------------------------------------------------------------
def extract_subjects(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    SubjectEntry
]:
    return [
        classify_subject(
            part,
            pair=pair,
        )
        for part in split_subject_text(
            text
        )
    ]


# ---------------------------------------------------------------------------
# FIND NEAREST GAP TYPE
# ---------------------------------------------------------------------------
def find_nearest_gap_type(
    text: str,
    *,
    formula: str,
) -> BandGapType | None:
    formula_matches = list(
        re.finditer(
            re.escape(
                formula
            ),
            text,
            flags=re.IGNORECASE,
        )
    )

    if not formula_matches:
        return None

    type_matches: list[
        tuple[
            int,
            BandGapType,
        ]
    ] = []

    for match in re.finditer(
        r"\bindirect\s+band\s+gap\b",
        text,
        flags=re.IGNORECASE,
    ):
        type_matches.append(
            (
                match.start(),
                BandGapType.INDIRECT,
            )
        )

    for match in re.finditer(
        r"\bdirect\s+band\s+gap\b",
        text,
        flags=re.IGNORECASE,
    ):
        type_matches.append(
            (
                match.start(),
                BandGapType.DIRECT,
            )
        )

    for match in re.finditer(
        r"\bindirect\s+transition\b",
        text,
        flags=re.IGNORECASE,
    ):
        type_matches.append(
            (
                match.start(),
                BandGapType.INDIRECT,
            )
        )

    for match in re.finditer(
        r"\bdirect\s+transition\b",
        text,
        flags=re.IGNORECASE,
    ):
        type_matches.append(
            (
                match.start(),
                BandGapType.DIRECT,
            )
        )

    if not type_matches:
        return None

    best_distance: int | None = None
    best_type: BandGapType | None = None

    for formula_match in formula_matches:
        for (
            type_position,
            gap_type,
        ) in type_matches:
            distance = abs(
                formula_match.start()
                - type_position
            )

            if distance > 300:
                continue

            if (
                best_distance is None
                or distance
                < best_distance
            ):
                best_distance = distance
                best_type = gap_type

    return best_type


# ---------------------------------------------------------------------------
# BUILD LIST CANDIDATES
# ---------------------------------------------------------------------------
def build_list_candidates(
    *,
    property_type: BandPropertyType,
    subjects_text: str,
    values_text: str,
    source_text: str,
    pair: PairRecord,
    full_text: str,
    extraction_basis: str,
) -> list[
    StructuredBandValue
]:
    subjects = extract_subjects(
        subjects_text,
        pair=pair,
    )

    values = extract_numeric_values(
        values_text
    )

    if (
        not subjects
        or len(
            subjects
        )
        != len(
            values
        )
    ):
        return []

    claim_context = (
        resolve_claim_context(
            source_text
        )
    )

    reference_scale = (
        resolve_reference_scale(
            source_text
        )
    )

    results: list[
        StructuredBandValue
    ] = []

    for (
        subject,
        value,
    ) in zip(
        subjects,
        values,
    ):
        if (
            subject.material_type
            is None
            or subject.formula
            is None
        ):
            continue

        band_gap_type = None

        if (
            property_type
            == BandPropertyType.BAND_GAP
        ):
            band_gap_type = (
                find_nearest_gap_type(
                    full_text,
                    formula=subject.formula,
                )
            )

        results.append(
            StructuredBandValue(
                property_type=(
                    property_type
                ),
                material_type=(
                    subject.material_type
                ),
                formula=(
                    subject.formula
                ),
                numeric_value=value,
                claim_context=(
                    claim_context
                ),
                reference_scale=(
                    reference_scale
                ),
                band_gap_type=(
                    band_gap_type
                ),
                source_text=(
                    clean_source_text(
                        source_text
                    )
                ),
                extraction_basis=(
                    extraction_basis
                ),
            )
        )

    return results


# ---------------------------------------------------------------------------
# EXTRACT LIST PATTERN
# ---------------------------------------------------------------------------
def extract_list_pattern(
    text: str,
    *,
    pair: PairRecord,
    property_type: BandPropertyType,
    pattern: re.Pattern,
    extraction_basis: str,
) -> list[
    StructuredBandValue
]:
    results: list[
        StructuredBandValue
    ] = []

    for match in pattern.finditer(
        text
    ):
        context_start = max(
            0,
            match.start() - 450,
        )

        context_end = min(
            len(
                text
            ),
            match.end() + 150,
        )

        context_text = text[
            context_start:
            context_end
        ]

        results.extend(
            build_list_candidates(
                property_type=(
                    property_type
                ),
                subjects_text=(
                    match.group(
                        "subjects"
                    )
                ),
                values_text=(
                    match.group(
                        "values"
                    )
                ),
                source_text=(
                    context_text
                ),
                pair=pair,
                full_text=text,
                extraction_basis=(
                    extraction_basis
                ),
            )
        )

    return results


# ---------------------------------------------------------------------------
# EXTRACT BAND GAP VALUE-FOR-FORMULA PAIRS
# ---------------------------------------------------------------------------
def extract_band_gap_value_for_formula(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    formula_pattern = (
        rf"(?:"
        rf"{re.escape(pair.psk_formula_reported)}"
        rf"|"
        rf"{re.escape(pair.tmd_formula_reported)}"
        rf")"
    )

    pair_pattern = re.compile(
        rf"(?P<value>{NUMERIC_PATTERN})"
        rf"\s*eV\s+for\s+"
        rf"(?P<formula>{formula_pattern})",
        flags=re.IGNORECASE,
    )

    results: list[
        StructuredBandValue
    ] = []

    for match in pair_pattern.finditer(
        normalized
    ):
        context_start = max(
            0,
            match.start() - 400,
        )

        context_end = min(
            len(
                normalized
            ),
            match.end() + 250,
        )

        context_text = normalized[
            context_start:
            context_end
        ]

        has_band_gap_context = (
            re.search(
                r"\b(?:"
                r"band\s*gap"
                r"|bandgap"
                r"|E\s*_?\s*g"
                r"|forbidden\s+bandwidth"
                r")\b",
                context_text,
                flags=re.IGNORECASE,
            )
            is not None
        )

        if not has_band_gap_context:
            continue

        formula = match.group(
            "formula"
        )

        material_type = (
            get_formula_material_type(
                formula,
                pair=pair,
            )
        )

        if material_type is None:
            continue

        canonical_formula = (
            get_material_formula(
                pair,
                material_type,
            )
        )

        results.append(
            StructuredBandValue(
                property_type=(
                    BandPropertyType
                    .BAND_GAP
                ),
                material_type=(
                    material_type
                ),
                formula=(
                    canonical_formula
                ),
                numeric_value=float(
                    match.group(
                        "value"
                    )
                ),
                claim_context=(
                    resolve_claim_context(
                        context_text
                    )
                ),
                reference_scale=None,
                band_gap_type=(
                    find_nearest_gap_type(
                        normalized,
                        formula=(
                            canonical_formula
                        ),
                    )
                ),
                source_text=(
                    clean_source_text(
                        context_text
                    )
                ),
                extraction_basis=(
                    "value_for_formula"
                ),
            )
        )

    return results


# ---------------------------------------------------------------------------
# EXTRACT PROPERTY VALUE WITH FORMULA IN PARENTHESES
# ---------------------------------------------------------------------------
def extract_parenthetical_band_edges(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    results: list[
        StructuredBandValue
    ] = []

    passages = re.split(
        r"(?<=[.!?])\s+|\n+",
        text,
    )

    for passage in passages:
        normalized = (
            normalize_pdf_numeric_text(
                passage
            )
        )

        property_type = None

        if re.search(
            r"\b(?:CB|conduction\s+band)\b",
            passage,
            flags=re.IGNORECASE,
        ):
            property_type = (
                BandPropertyType.CBM
            )

        if (
            property_type is None
            and re.search(
                r"\b(?:VB|valence\s+band)\b",
                passage,
                flags=re.IGNORECASE,
            )
        ):
            property_type = (
                BandPropertyType.VBM
            )

        if property_type is None:
            continue

        pattern = re.compile(
            rf"(?P<value>{NUMERIC_PATTERN})"
            rf"\s*eV\s*"
            rf"\(\s*"
            rf"(?P<formula>"
            rf"{re.escape(pair.psk_formula_reported)}"
            rf"|{re.escape(pair.tmd_formula_reported)}"
            rf")"
            rf"\s*\)",
            flags=re.IGNORECASE,
        )

        for match in pattern.finditer(
            normalized
        ):
            formula = match.group(
                "formula"
            )

            material_type = (
                get_formula_material_type(
                    formula,
                    pair=pair,
                )
            )

            if material_type is None:
                continue

            results.append(
                StructuredBandValue(
                    property_type=(
                        property_type
                    ),
                    material_type=(
                        material_type
                    ),
                    formula=(
                        get_material_formula(
                            pair,
                            material_type,
                        )
                    ),
                    numeric_value=float(
                        match.group(
                            "value"
                        )
                    ),
                    claim_context=(
                        resolve_claim_context(
                            passage
                        )
                    ),
                    reference_scale=(
                        resolve_reference_scale(
                            passage
                        )
                    ),
                    band_gap_type=None,
                    source_text=(
                        clean_source_text(
                            passage
                        )
                    ),
                    extraction_basis=(
                        "value_formula_parentheses"
                    ),
                )
            )

    return results


# ---------------------------------------------------------------------------
# EXTRACT LOCAL FORMULA BAND EDGE
# ---------------------------------------------------------------------------
def extract_local_formula_band_edges(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    results: list[
        StructuredBandValue
    ] = []

    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    formula_pattern = (
        rf"(?:"
        rf"{re.escape(pair.psk_formula_reported)}"
        rf"|"
        rf"{re.escape(pair.tmd_formula_reported)}"
        rf")"
    )

    patterns = [
        (
            BandPropertyType.CBM,
            re.compile(
                rf"(?:"
                rf"CB(?:\s+potential(?:\s+position)?)?"
                rf"|conduction\s+band"
                rf")"
                rf"\s+of\s+"
                rf"(?P<formula>{formula_pattern})"
                rf"\s*\("
                rf"(?P<value>{NUMERIC_PATTERN})"
                rf"\s*eV",
                flags=re.IGNORECASE,
            ),
        ),
        (
            BandPropertyType.VBM,
            re.compile(
                rf"(?:"
                rf"VB(?:\s+potential(?:\s+position)?)?"
                rf"|valence\s+band"
                rf")"
                rf"\s+of\s+"
                rf"(?P<formula>{formula_pattern})"
                rf"\s*\("
                rf"(?P<value>{NUMERIC_PATTERN})"
                rf"\s*eV",
                flags=re.IGNORECASE,
            ),
        ),
    ]

    for (
        property_type,
        pattern,
    ) in patterns:
        for match in pattern.finditer(
            normalized
        ):
            formula = match.group(
                "formula"
            )

            material_type = (
                get_formula_material_type(
                    formula,
                    pair=pair,
                )
            )

            if material_type is None:
                continue

            start = max(
                0,
                match.start() - 150,
            )

            end = min(
                len(
                    normalized
                ),
                match.end() + 150,
            )

            source_text = normalized[
                start:
                end
            ]

            results.append(
                StructuredBandValue(
                    property_type=(
                        property_type
                    ),
                    material_type=(
                        material_type
                    ),
                    formula=(
                        get_material_formula(
                            pair,
                            material_type,
                        )
                    ),
                    numeric_value=float(
                        match.group(
                            "value"
                        )
                    ),
                    claim_context=(
                        resolve_claim_context(
                            source_text
                        )
                    ),
                    reference_scale=(
                        resolve_reference_scale(
                            source_text
                        )
                    ),
                    band_gap_type=None,
                    source_text=(
                        clean_source_text(
                            source_text
                        )
                    ),
                    extraction_basis=(
                        "local_formula_band_edge"
                    ),
                )
            )

    return results


# ---------------------------------------------------------------------------
# EXTRACT PAIRED CB AND VB STATEMENTS
# ---------------------------------------------------------------------------
def extract_paired_cb_vb_statements(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    formula_pattern = (
        rf"(?:"
        rf"{re.escape(pair.psk_formula_reported)}"
        rf"|"
        rf"{re.escape(pair.tmd_formula_reported)}"
        rf")"
    )

    pattern = re.compile(
        rf"\bCB\s+and\s+VB\s+of\s+"
        rf"(?P<formula>{formula_pattern})"
        rf"\s+are\s+"
        rf"(?P<cb>{NUMERIC_PATTERN})"
        rf"\s*eV\s+and\s+"
        rf"(?P<vb>{NUMERIC_PATTERN})"
        rf"\s*eV",
        flags=re.IGNORECASE,
    )

    results: list[
        StructuredBandValue
    ] = []

    for match in pattern.finditer(
        normalized
    ):
        formula = match.group(
            "formula"
        )

        material_type = (
            get_formula_material_type(
                formula,
                pair=pair,
            )
        )

        if material_type is None:
            continue

        canonical_formula = (
            get_material_formula(
                pair,
                material_type,
            )
        )

        context_start = max(
            0,
            match.start() - 250,
        )

        context_end = min(
            len(
                normalized
            ),
            match.end() + 250,
        )

        source_text = normalized[
            context_start:
            context_end
        ]

        common_kwargs = {
            "material_type": (
                material_type
            ),
            "formula": (
                canonical_formula
            ),
            "claim_context": (
                resolve_claim_context(
                    source_text
                )
            ),
            "reference_scale": (
                resolve_reference_scale(
                    source_text
                )
            ),
            "band_gap_type": None,
            "source_text": (
                clean_source_text(
                    source_text
                )
            ),
            "extraction_basis": (
                "paired_cb_vb_statement"
            ),
        }

        results.append(
            StructuredBandValue(
                property_type=(
                    BandPropertyType.CBM
                ),
                numeric_value=float(
                    match.group(
                        "cb"
                    )
                ),
                **common_kwargs,
            )
        )

        results.append(
            StructuredBandValue(
                property_type=(
                    BandPropertyType.VBM
                ),
                numeric_value=float(
                    match.group(
                        "vb"
                    )
                ),
                **common_kwargs,
            )
        )

    return results


# ---------------------------------------------------------------------------
# EXTRACT VB-XPS RESPECTIVELY LIST
# ---------------------------------------------------------------------------
def extract_vb_xps_respectively_list(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    formula_pattern = (
        rf"(?:"
        rf"{re.escape(pair.psk_formula_reported)}"
        rf"|"
        rf"{re.escape(pair.tmd_formula_reported)}"
        rf")"
    )

    pattern = re.compile(
        rf"(?:energy\s+levels?\s+of\s+)?"
        rf"(?:the\s+)?VB\s+of\s+"
        rf"(?P<formula_1>{formula_pattern})"
        rf"\s+and\s+"
        rf"(?P<formula_2>{formula_pattern})"
        rf"\s+(?:are|were)\s+"
        rf"(?P<value_1>{NUMERIC_PATTERN})"
        rf"\s*eV\s+and\s+"
        rf"(?P<value_2>{NUMERIC_PATTERN})"
        rf"\s*eV"
        rf"\s*,?\s*respectively\b",
        flags=re.IGNORECASE,
    )

    results: list[
        StructuredBandValue
    ] = []

    for match in pattern.finditer(
        normalized
    ):
        context_start = max(
            0,
            match.start() - 250,
        )

        context_end = min(
            len(
                normalized
            ),
            match.end() + 150,
        )

        source_text = normalized[
            context_start:
            context_end
        ]

        formula_value_pairs = [
            (
                match.group(
                    "formula_1"
                ),
                float(
                    match.group(
                        "value_1"
                    )
                ),
            ),
            (
                match.group(
                    "formula_2"
                ),
                float(
                    match.group(
                        "value_2"
                    )
                ),
            ),
        ]

        for (
            formula,
            numeric_value,
        ) in formula_value_pairs:
            material_type = (
                get_formula_material_type(
                    formula,
                    pair=pair,
                )
            )

            if material_type is None:
                continue

            results.append(
                StructuredBandValue(
                    property_type=(
                        BandPropertyType.VBM
                    ),
                    material_type=(
                        material_type
                    ),
                    formula=(
                        get_material_formula(
                            pair,
                            material_type,
                        )
                    ),
                    numeric_value=(
                        numeric_value
                    ),
                    claim_context=(
                        resolve_claim_context(
                            source_text
                        )
                    ),
                    reference_scale=(
                        resolve_reference_scale(
                            source_text
                        )
                    ),
                    band_gap_type=None,
                    source_text=(
                        clean_source_text(
                            source_text
                        )
                    ),
                    extraction_basis=(
                        "vb_xps_respectively_list"
                    ),
                )
            )

    return results


# ---------------------------------------------------------------------------
# EXTRACT SIMPLE CB RESPECTIVELY PAIRS
# ---------------------------------------------------------------------------
def extract_simple_cb_respectively_pairs(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    formula_pattern = (
        rf"(?:"
        rf"{re.escape(pair.psk_formula_reported)}"
        rf"|"
        rf"{re.escape(pair.tmd_formula_reported)}"
        rf")"
    )

    pattern = re.compile(
        rf"(?:"
        rf"conduction\s+band"
        rf"(?:\s*\(CB\))?"
        rf"|CB"
        rf")"
        rf"\s+(?:potentials?|positions?)"
        rf"\s+of\s+"
        rf"(?P<formula_1>{formula_pattern})"
        rf"\s+and\s+"
        rf"(?P<formula_2>{formula_pattern})"
        rf".*?"
        rf"(?:are|were)"
        rf".*?"
        rf"(?P<value_1>{NUMERIC_PATTERN})"
        rf"\s*eV?"
        rf"\s+and\s+"
        rf"(?P<value_2>{NUMERIC_PATTERN})"
        rf"\s*eV?"
        rf".*?"
        rf"\bNHE\b"
        rf".*?"
        rf"\brespectively\b",
        flags=(
            re.IGNORECASE
            | re.DOTALL
        ),
    )

    results: list[
        StructuredBandValue
    ] = []

    for match in pattern.finditer(
        normalized
    ):
        context_start = max(
            0,
            match.start() - 200,
        )

        context_end = min(
            len(
                normalized
            ),
            match.end() + 150,
        )

        source_text = normalized[
            context_start:
            context_end
        ]

        formula_value_pairs = [
            (
                match.group(
                    "formula_1"
                ),
                float(
                    match.group(
                        "value_1"
                    )
                ),
            ),
            (
                match.group(
                    "formula_2"
                ),
                float(
                    match.group(
                        "value_2"
                    )
                ),
            ),
        ]

        for (
            formula,
            numeric_value,
        ) in formula_value_pairs:
            material_type = (
                get_formula_material_type(
                    formula,
                    pair=pair,
                )
            )

            if material_type is None:
                continue

            results.append(
                StructuredBandValue(
                    property_type=(
                        BandPropertyType.CBM
                    ),
                    material_type=(
                        material_type
                    ),
                    formula=(
                        get_material_formula(
                            pair,
                            material_type,
                        )
                    ),
                    numeric_value=(
                        numeric_value
                    ),
                    claim_context=(
                        resolve_claim_context(
                            source_text
                        )
                    ),
                    reference_scale=(
                        BandReferenceScale.NHE
                    ),
                    band_gap_type=None,
                    source_text=(
                        clean_source_text(
                            source_text
                        )
                    ),
                    extraction_basis=(
                        "simple_cb_respectively_pair"
                    ),
                )
            )

    return results


# ---------------------------------------------------------------------------
# DEDUPLICATE BAND VALUES
# ---------------------------------------------------------------------------
def deduplicate_band_values(
    values: list[
        StructuredBandValue
    ],
) -> list[
    StructuredBandValue
]:
    seen: set[
        tuple[
            BandPropertyType,
            MaterialType,
            str,
            float,
        ]
    ] = set()

    results: list[
        StructuredBandValue
    ] = []

    for value in values:
        key = (
            value.property_type,
            value.material_type,
            value.formula,
            round(
                value.numeric_value,
                6,
            ),
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        results.append(
            value
        )

    return results


# ---------------------------------------------------------------------------
# EXTRACT STRUCTURED BAND VALUES
# ---------------------------------------------------------------------------
def extract_structured_band_values(
    text: str,
    *,
    pair: PairRecord,
) -> list[
    StructuredBandValue
]:
    normalized = (
        normalize_pdf_numeric_text(
            text
        )
    )

    results: list[
        StructuredBandValue
    ] = []

    results.extend(
        extract_list_pattern(
            normalized,
            pair=pair,
            property_type=(
                BandPropertyType.BAND_GAP
            ),
            pattern=(
                BAND_GAP_LIST_PATTERN
            ),
            extraction_basis=(
                "band_gap_respectively_list"
            ),
        )
    )

    results.extend(
        extract_list_pattern(
            normalized,
            pair=pair,
            property_type=(
                BandPropertyType.CBM
            ),
            pattern=(
                CB_LIST_PATTERN
            ),
            extraction_basis=(
                "cb_respectively_list"
            ),
        )
    )

    results.extend(
        extract_simple_cb_respectively_pairs(
            normalized,
            pair=pair,
        )
    )

    results.extend(
        extract_list_pattern(
            normalized,
            pair=pair,
            property_type=(
                BandPropertyType.VBM
            ),
            pattern=(
                VB_LIST_PATTERN
            ),
            extraction_basis=(
                "vb_respectively_list"
            ),
        )
    )

    results.extend(
        extract_vb_xps_respectively_list(
            normalized,
            pair=pair,
        )
    )

    results.extend(
        extract_paired_cb_vb_statements(
            normalized,
            pair=pair,
        )
    )

    results.extend(
        extract_band_gap_value_for_formula(
            normalized,
            pair=pair,
        )
    )

    results.extend(
        extract_parenthetical_band_edges(
            normalized,
            pair=pair,
        )
    )

    results.extend(
        extract_local_formula_band_edges(
            normalized,
            pair=pair,
        )
    )

    return (
        deduplicate_band_values(
            results
        )
    )

