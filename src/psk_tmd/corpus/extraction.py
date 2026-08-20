import re

from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    CharacterizationRole,
    ChargeTransferClass,
    EvidenceContextType,
    MechanismLabel,
    PaperSectionRole,
)
from psk_tmd.common.text_utils import (
    normalize_whitespace,
)
from psk_tmd.corpus.passages import (
    PassageCategory,
    RelevantPassage,
)


# ---------------------------------------------------------------------------
# MECHANISM CLAIM CANDIDATE
# ---------------------------------------------------------------------------
class MechanismClaimCandidate(BaseModel):
    mechanism_reported: str
    mechanism_normalized: MechanismLabel

    charge_transfer_class: (
        ChargeTransferClass | None
    ) = None

    claim_explicit: bool = True

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    source_text: str

    score: float = Field(
        ge=0.0,
    )


# ---------------------------------------------------------------------------
# CHARACTERIZATION CANDIDATE
# ---------------------------------------------------------------------------
class CharacterizationCandidate(BaseModel):
    evidence_type: str

    characterization_role: (
        CharacterizationRole
    )

    mechanism_discriminating: bool = False

    requires_context: bool = False

    required_context: list[
        EvidenceContextType
    ] = Field(
        default_factory=list,
    )

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    matched_terms: list[str] = Field(
        default_factory=list,
    )

    source_text: str

    score: float = Field(
        ge=0.0,
    )


# ---------------------------------------------------------------------------
# MECHANISM EVIDENCE CANDIDATE
# ---------------------------------------------------------------------------
class MechanismEvidenceCandidate(BaseModel):
    evidence_type: str

    characterization_role: (
        CharacterizationRole
    )

    mechanism_discriminating: bool = False

    requires_context: bool = False

    required_context: list[
        EvidenceContextType
    ] = Field(
        default_factory=list,
    )

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_title: str | None = None

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    matched_terms: list[str] = Field(
        default_factory=list,
    )

    source_text: str

    score: float = Field(
        ge=0.0,
    )


# ---------------------------------------------------------------------------
# MECHANISM EXTRACTION RESULT
# ---------------------------------------------------------------------------
class MechanismExtractionResult(BaseModel):
    mechanism_claims: list[
        MechanismClaimCandidate
    ] = Field(
        default_factory=list,
    )

    characterization_candidates: list[
        CharacterizationCandidate
    ] = Field(
        default_factory=list,
    )

    mechanism_evidence_candidates: list[
        MechanismEvidenceCandidate
    ] = Field(
        default_factory=list,
    )


# ---------------------------------------------------------------------------
# ELIGIBLE MECHANISM SECTIONS
# ---------------------------------------------------------------------------
MECHANISM_ELIGIBLE_SECTIONS: set[
    PaperSectionRole
] = {
    PaperSectionRole.ABSTRACT,
    PaperSectionRole.RESULTS,
    PaperSectionRole.MECHANISM,
    PaperSectionRole.CONCLUSION,
    PaperSectionRole.OTHER,
}


# ---------------------------------------------------------------------------
# EXCLUDED MECHANISM SECTIONS
# ---------------------------------------------------------------------------
MECHANISM_EXCLUDED_SECTIONS: set[
    PaperSectionRole
] = {
    PaperSectionRole.INTRODUCTION,
    PaperSectionRole.EXPERIMENTAL,
    PaperSectionRole.REFERENCES,
}


# ---------------------------------------------------------------------------
# SECTION PRIORITY
# ---------------------------------------------------------------------------
SECTION_PRIORITY: dict[
    PaperSectionRole,
    float,
] = {
    PaperSectionRole.MECHANISM: 5.0,
    PaperSectionRole.RESULTS: 3.0,
    PaperSectionRole.CONCLUSION: 2.5,
    PaperSectionRole.ABSTRACT: 1.5,
    PaperSectionRole.OTHER: 0.5,
    PaperSectionRole.INTRODUCTION: 0.0,
    PaperSectionRole.EXPERIMENTAL: 0.0,
    PaperSectionRole.REFERENCES: 0.0,
}


# ---------------------------------------------------------------------------
# MECHANISM PATTERNS
# ---------------------------------------------------------------------------
MECHANISM_PATTERNS: tuple[
    tuple[
        re.Pattern[str],
        MechanismLabel,
    ],
    ...,
] = (
    (
        re.compile(
            r"\bz\s*-\s*scheme\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.Z_SCHEME,
    ),
    (
        re.compile(
            r"\bz\s+scheme\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.Z_SCHEME,
    ),
    (
        re.compile(
            r"\bs\s*-\s*scheme\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.S_SCHEME,
    ),
    (
        re.compile(
            r"\bs\s+scheme\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.S_SCHEME,
    ),
    (
        re.compile(
            r"\btype\s*-\s*i{3}\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_III,
    ),
    (
        re.compile(
            r"\btype\s+iii\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_III,
    ),
    (
        re.compile(
            r"\btype\s*-\s*ii\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_II,
    ),
    (
        re.compile(
            r"\btype\s+ii\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_II,
    ),
    (
        re.compile(
            r"\btype\s*-\s*i\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_I,
    ),
    (
        re.compile(
            r"\btype\s+i\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.TYPE_I,
    ),
    (
        re.compile(
            r"\bp\s*-\s*n\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.P_N,
    ),
    (
        re.compile(
            r"\bp\s+n\s+junction\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.P_N,
    ),
    (
        re.compile(
            r"\bschottky\s+junction\b",
            flags=re.IGNORECASE,
        ),
        MechanismLabel.SCHOTTKY,
    ),
)


# ---------------------------------------------------------------------------
# AMBIGUOUS BAND-TYPE LABELS
# ---------------------------------------------------------------------------
AMBIGUOUS_BAND_TYPE_LABELS: set[
    MechanismLabel
] = {
    MechanismLabel.TYPE_I,
    MechanismLabel.TYPE_II,
    MechanismLabel.TYPE_III,
}


# ---------------------------------------------------------------------------
# BET CONTEXT TERMS
# ---------------------------------------------------------------------------
BET_CONTEXT_TERMS: tuple[str, ...] = (
    "bet",
    "brunauer-emmett-teller",
    "brunauer–emmett–teller",
    "adsorption isotherm",
    "adsorption isotherms",
    "desorption isotherm",
    "desorption isotherms",
    "adsorption-desorption",
    "adsorption–desorption",
    "nitrogen adsorption",
    "n2 adsorption",
    "n₂ adsorption",
    "specific surface area",
    "surface area",
    "pore volume",
    "pore size",
    "pore diameter",
    "hysteresis loop",
    "relative pressure",
    "p/p0",
    "p/p₀",
)


# ---------------------------------------------------------------------------
# CHARACTERIZATION KEYWORDS
# ---------------------------------------------------------------------------
CHARACTERIZATION_KEYWORDS: dict[
    str,
    tuple[str, ...],
] = {
    "xps": (
        "xps",
        "x-ray photoelectron spectroscopy",
        "binding energy",
        "binding-energy",
    ),
    "mott_schottky": (
        "mott-schottky",
        "mott schottky",
        "flat-band",
        "flat band",
    ),
    "band_alignment": (
        "conduction band",
        "valence band",
        "band alignment",
        "band position",
        "band positions",
        "cb potential",
        "vb potential",
        "band edge",
        "band edges",
    ),
    "photocurrent": (
        "photocurrent",
    ),
    "eis": (
        "electrochemical impedance",
        "impedance spectroscopy",
        "eis",
        "nyquist",
    ),
    "lsv": (
        "linear sweep voltammetry",
        "lsv",
        "overpotential",
    ),
    "spm": (
        "surface photovoltage",
        "photovoltage",
        "spv",
    ),
    "photoluminescence": (
        "photoluminescence",
        "pl spectrum",
        "pl spectra",
        "pl intensity",
    ),
    "radical_trapping": (
        "radical trapping",
        "radical scavenging",
        "scavenger",
        "scavengers",
        "scavenger test",
        "scavenger tests",
        "scavenging",
        "quenching experiment",
        "quenching experiments",
        "trapping experiment",
        "trapping experiments",
    ),
    "esr": (
        "electron spin resonance",
        "electron paramagnetic resonance",
        "esr",
        "epr",
        "dmpo",
    ),
    "work_function": (
        "work function",
    ),
    "kelvin_probe": (
        "kelvin probe",
        "kpfm",
        "kelvin probe force microscopy",
    ),
    "photodeposition": (
        "photodeposition",
        "photo-deposition",
        "photodeposited",
        "photo-deposited",
    ),
}


# ---------------------------------------------------------------------------
# RESULT-BEARING TERMS
# ---------------------------------------------------------------------------
RESULT_BEARING_TERMS: tuple[str, ...] = (
    "higher",
    "lower",
    "smaller",
    "larger",
    "increase",
    "increased",
    "decrease",
    "decreased",
    "shift",
    "shifted",
    "shifts",
    "migrate",
    "migrated",
    "migration",
    "transfer",
    "transferred",
    "redistribution",
    "electron density",
    "determined",
    "calculated",
    "indicates",
    "indicating",
    "demonstrates",
    "demonstrating",
    "proves",
    "reveals",
    "revealing",
    "supports",
    "consistent with",
    "recombination",
    "separation",
    "generated",
    "detected",
    "response",
    "potential",
    "binding energy",
)


# ---------------------------------------------------------------------------
# DIRECTIONAL CHARGE TERMS
# ---------------------------------------------------------------------------
DIRECTIONAL_CHARGE_TERMS: tuple[str, ...] = (
    "electron migration",
    "electrons migrated",
    "electrons transfer",
    "electron transfer",
    "transferred from",
    "migrated from",
    "charge transfer direction",
    "electron redistribution",
    "interfacial electron transfer",
    "higher binding energy",
    "lower binding energy",
    "electron density",
    "built-in electric field",
    "internal electric field",
)


# ---------------------------------------------------------------------------
# CHARGE-SEPARATION TERMS
# ---------------------------------------------------------------------------
CHARGE_SEPARATION_TERMS: tuple[str, ...] = (
    "charge separation",
    "carrier separation",
    "electron-hole separation",
    "electron hole separation",
    "recombination rate",
    "recombination probability",
    "charge recombination",
    "carrier recombination",
    "charge-transfer resistance",
    "charge transfer resistance",
    "carrier lifetime",
    "charge lifetime",
    "conductivity",
)


# ---------------------------------------------------------------------------
# RADICAL INTERPRETATION TERMS
# ---------------------------------------------------------------------------
RADICAL_INTERPRETATION_TERMS: tuple[
    str,
    ...
] = (
    "active species",
    "radical",
    "radicals",
    "scavenger",
    "scavenging",
    "trapping",
    "quenching",
    "superoxide",
    "hydroxyl",
    "•o2",
    "o2•",
    "o2−",
    "•oh",
    "oh•",
)


# ---------------------------------------------------------------------------
# METHODS-ONLY TERMS
# ---------------------------------------------------------------------------
METHODS_ONLY_TERMS: tuple[str, ...] = (
    "was performed",
    "were performed",
    "was measured",
    "were measured",
    "was obtained",
    "were obtained",
    "was acquired",
    "were acquired",
    "was used",
    "were used",
    "instrument",
    "workstation",
    "spectrometer",
)


# ---------------------------------------------------------------------------
# DEDUPLICATE PASSAGES
# ---------------------------------------------------------------------------
def deduplicate_passages(
    passages: list[RelevantPassage],
) -> list[RelevantPassage]:
    unique_passages: list[
        RelevantPassage
    ] = []

    seen: set[
        tuple[
            int | None,
            str,
        ]
    ] = set()

    for passage in passages:
        key = (
            passage.page_number,
            passage.text,
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        unique_passages.append(
            passage
        )

    return unique_passages


# ---------------------------------------------------------------------------
# CHECK MECHANISM SECTION ELIGIBILITY
# ---------------------------------------------------------------------------
def is_mechanism_section_eligible(
    passage: RelevantPassage,
) -> bool:
    return (
        passage.section_role
        in MECHANISM_ELIGIBLE_SECTIONS
    )


# ---------------------------------------------------------------------------
# FIND MECHANISM CLAIM
# ---------------------------------------------------------------------------
def find_mechanism_claim(
    text: str,
) -> tuple[
    str,
    MechanismLabel,
] | None:
    clean_text = normalize_whitespace(
        text
    )

    bet_context = is_bet_context(
        clean_text
    )

    for pattern, mechanism_label in (
        MECHANISM_PATTERNS
    ):
        match = pattern.search(
            clean_text
        )

        if match is None:
            continue

        if (
            mechanism_label
            in AMBIGUOUS_BAND_TYPE_LABELS
            and bet_context
        ):
            continue

        return (
            match.group(0),
            mechanism_label,
        )

    return None


# ---------------------------------------------------------------------------
# CHECK BET CONTEXT
# ---------------------------------------------------------------------------
def is_bet_context(
    text: str,
) -> bool:
    lower_text = text.lower()

    return any(
        term.lower() in lower_text
        for term in BET_CONTEXT_TERMS
    )


# ---------------------------------------------------------------------------
# FIND MATCHED TERMS
# ---------------------------------------------------------------------------
def find_matched_terms(
    text: str,
    keywords: tuple[str, ...],
) -> list[str]:
    lower_text = text.lower()

    matched_terms: list[str] = []

    for keyword in keywords:
        if keyword.lower() in lower_text:
            matched_terms.append(
                keyword
            )

    return matched_terms


# ---------------------------------------------------------------------------
# COUNT TERM MATCHES
# ---------------------------------------------------------------------------
def count_term_matches(
    text: str,
    terms: tuple[str, ...],
) -> int:
    lower_text = text.lower()

    return sum(
        1
        for term in terms
        if term.lower() in lower_text
    )


# ---------------------------------------------------------------------------
# SECTION SCORE
# ---------------------------------------------------------------------------
def get_section_score(
    section_role: PaperSectionRole,
) -> float:
    return SECTION_PRIORITY.get(
        section_role,
        0.0,
    )


# ---------------------------------------------------------------------------
# CLASSIFY CHARACTERIZATION ROLE
# ---------------------------------------------------------------------------
def classify_characterization_role(
    evidence_type: str,
    text: str,
    section_role: PaperSectionRole,
) -> tuple[
    CharacterizationRole,
    bool,
    bool,
    list[EvidenceContextType],
]:
    lower_text = text.lower()

    if evidence_type == "radical_trapping":
        return (
            CharacterizationRole.MECHANISM_ASSESSMENT,
            True,
            True,
            [
                EvidenceContextType.BAND_EDGES,
                EvidenceContextType.REDOX_POTENTIALS,
            ],
        )

    if evidence_type == "esr":
        return (
            CharacterizationRole.MECHANISM_ASSESSMENT,
            True,
            True,
            [
                EvidenceContextType.BAND_EDGES,
                EvidenceContextType.REDOX_POTENTIALS,
            ],
        )

    if evidence_type in {
        "mott_schottky",
        "band_alignment",
    }:
        return (
            CharacterizationRole.BAND_STRUCTURE,
            False,
            False,
            [],
        )

    if evidence_type in {
        "photocurrent",
        "eis",
        "lsv",
        "spm",
        "photoluminescence",
    }:
        return (
            CharacterizationRole.CHARGE_SEPARATION_SUPPORT,
            False,
            False,
            [],
        )

    if evidence_type == "xps":
        has_directional_signal = any(
            term in lower_text
            for term in (
                "higher binding energy",
                "lower binding energy",
                "electron migration",
                "electrons migrated",
                "electron transfer",
                "transferred from",
                "migrated from",
                "electron density",
                "charge redistribution",
            )
        )

        if (
            has_directional_signal
            and section_role
            in {
                PaperSectionRole.RESULTS,
                PaperSectionRole.MECHANISM,
                PaperSectionRole.CONCLUSION,
            }
        ):
            return (
                CharacterizationRole.MECHANISM_ASSESSMENT,
                True,
                True,
                [
                    EvidenceContextType.BAND_ALIGNMENT,
                ],
            )

        return (
            CharacterizationRole.STRUCTURAL_CHARACTERIZATION,
            False,
            False,
            [],
        )

    if evidence_type in {
        "work_function",
        "kelvin_probe",
    }:
        has_mechanistic_interpretation = any(
            term in lower_text
            for term in (
                "electron transfer",
                "charge transfer",
                "built-in electric field",
                "internal electric field",
                "work function difference",
                "contact potential",
            )
        )

        if has_mechanistic_interpretation:
            return (
                CharacterizationRole.MECHANISM_ASSESSMENT,
                True,
                True,
                [
                    EvidenceContextType.BAND_ALIGNMENT,
                ],
            )

        return (
            CharacterizationRole.BAND_STRUCTURE,
            False,
            False,
            [],
        )

    if evidence_type == "photodeposition":
        return (
            CharacterizationRole.MECHANISM_ASSESSMENT,
            True,
            True,
            [
                EvidenceContextType.BAND_EDGES,
            ],
        )

    return (
        CharacterizationRole.OTHER,
        False,
        False,
        [],
    )


# ---------------------------------------------------------------------------
# SCORE MECHANISM CLAIM
# ---------------------------------------------------------------------------
def score_mechanism_claim(
    text: str,
    section_role: PaperSectionRole,
) -> float:
    score = 1.0

    score += get_section_score(
        section_role
    )

    lower_text = text.lower()

    if "mechanism" in lower_text:
        score += 1.0

    if (
        "electron transfer" in lower_text
        or "charge transfer" in lower_text
    ):
        score += 1.0

    if (
        "conduction band" in lower_text
        and "valence band" in lower_text
    ):
        score += 1.0

    if (
        "recombination" in lower_text
        and "electron" in lower_text
        and "hole" in lower_text
    ):
        score += 2.0

    if "in summary" in lower_text:
        score += 0.5

    if len(text) < 80:
        score -= 0.5

    return max(
        score,
        0.0,
    )


# ---------------------------------------------------------------------------
# SCORE CHARACTERIZATION CANDIDATE
# ---------------------------------------------------------------------------
def score_characterization_candidate(
    evidence_type: str,
    text: str,
    matched_terms: list[str],
    section_role: PaperSectionRole,
    characterization_role: CharacterizationRole,
) -> float:
    score = float(
        len(matched_terms)
    )

    score += get_section_score(
        section_role
    )

    score += (
        0.75
        * count_term_matches(
            text,
            RESULT_BEARING_TERMS,
        )
    )

    score -= (
        1.0
        * count_term_matches(
            text,
            METHODS_ONLY_TERMS,
        )
    )

    if (
        characterization_role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    ):
        score += 3.0

    elif (
        characterization_role
        == CharacterizationRole.BAND_STRUCTURE
    ):
        score += 1.0

    lower_text = text.lower()

    if evidence_type == "radical_trapping":
        score += (
            1.0
            * count_term_matches(
                text,
                RADICAL_INTERPRETATION_TERMS,
            )
        )

    if evidence_type == "esr":
        if "dmpo" in lower_text:
            score += 2.0

        if (
            "radical" in lower_text
            or "response signal" in lower_text
            or "response signals"
            in lower_text
        ):
            score += 2.0

    if evidence_type == "xps":
        score += (
            1.0
            * count_term_matches(
                text,
                DIRECTIONAL_CHARGE_TERMS,
            )
        )

    if evidence_type in {
        "photocurrent",
        "eis",
        "lsv",
        "spm",
        "photoluminescence",
    }:
        score += (
            0.5
            * count_term_matches(
                text,
                CHARGE_SEPARATION_TERMS,
            )
        )

    return max(
        score,
        0.0,
    )


# ---------------------------------------------------------------------------
# EXTRACT RAW MECHANISM CLAIMS
# ---------------------------------------------------------------------------
def extract_raw_mechanism_claims(
    passages: list[RelevantPassage],
) -> list[MechanismClaimCandidate]:
    candidates: list[
        MechanismClaimCandidate
    ] = []

    for passage in deduplicate_passages(
        passages
    ):
        if not is_mechanism_section_eligible(
            passage
        ):
            continue

        claim = find_mechanism_claim(
            passage.text
        )

        if claim is None:
            continue

        reported_phrase, normalized = claim

        candidates.append(
            MechanismClaimCandidate(
                mechanism_reported=(
                    reported_phrase
                ),
                mechanism_normalized=(
                    normalized
                ),
                charge_transfer_class=None,
                claim_explicit=True,
                page_number=(
                    passage.page_number
                ),
                section_title=(
                    passage.section_title
                ),
                section_role=(
                    passage.section_role
                ),
                source_text=passage.text,
                score=score_mechanism_claim(
                    text=passage.text,
                    section_role=(
                        passage.section_role
                    ),
                ),
            )
        )

    return candidates


# ---------------------------------------------------------------------------
# CONSOLIDATE MECHANISM CLAIMS
# ---------------------------------------------------------------------------
def consolidate_mechanism_claims(
    candidates: list[
        MechanismClaimCandidate
    ],
) -> list[MechanismClaimCandidate]:
    best_by_label: dict[
        MechanismLabel,
        MechanismClaimCandidate,
    ] = {}

    for candidate in candidates:
        label = (
            candidate.mechanism_normalized
        )

        current = best_by_label.get(
            label
        )

        if (
            current is None
            or candidate.score
            > current.score
        ):
            best_by_label[
                label
            ] = candidate

    return sorted(
        best_by_label.values(),
        key=lambda candidate: (
            -candidate.score,
            candidate.page_number
            if candidate.page_number
            is not None
            else 9999,
        ),
    )


# ---------------------------------------------------------------------------
# EXTRACT CHARACTERIZATION CANDIDATES
# ---------------------------------------------------------------------------
def extract_characterization_candidates(
    passages: list[RelevantPassage],
) -> list[CharacterizationCandidate]:
    candidates: list[
        CharacterizationCandidate
    ] = []

    for passage in deduplicate_passages(
        passages
    ):
        if not is_mechanism_section_eligible(
            passage
        ):
            continue

        if (
            passage.category
            != PassageCategory.MECHANISM
        ):
            continue

        for evidence_type, keywords in (
            CHARACTERIZATION_KEYWORDS.items()
        ):
            matched_terms = (
                find_matched_terms(
                    passage.text,
                    keywords,
                )
            )

            if not matched_terms:
                continue

            (
                characterization_role,
                mechanism_discriminating,
                requires_context,
                required_context,
            ) = classify_characterization_role(
                evidence_type=(
                    evidence_type
                ),
                text=passage.text,
                section_role=(
                    passage.section_role
                ),
            )

            score = (
                score_characterization_candidate(
                    evidence_type=(
                        evidence_type
                    ),
                    text=passage.text,
                    matched_terms=matched_terms,
                    section_role=(
                        passage.section_role
                    ),
                    characterization_role=(
                        characterization_role
                    ),
                )
            )

            candidates.append(
                CharacterizationCandidate(
                    evidence_type=(
                        evidence_type
                    ),
                    characterization_role=(
                        characterization_role
                    ),
                    mechanism_discriminating=(
                        mechanism_discriminating
                    ),
                    requires_context=(
                        requires_context
                    ),
                    required_context=(
                        required_context
                    ),
                    page_number=(
                        passage.page_number
                    ),
                    section_title=(
                        passage.section_title
                    ),
                    section_role=(
                        passage.section_role
                    ),
                    matched_terms=(
                        matched_terms
                    ),
                    source_text=(
                        passage.text
                    ),
                    score=score,
                )
            )

    return candidates


# ---------------------------------------------------------------------------
# CONSOLIDATE CHARACTERIZATION CANDIDATES
# ---------------------------------------------------------------------------
def consolidate_characterization_candidates(
    candidates: list[
        CharacterizationCandidate
    ],
) -> list[CharacterizationCandidate]:
    best_by_type: dict[
        str,
        CharacterizationCandidate,
    ] = {}

    for candidate in candidates:
        evidence_type = (
            candidate.evidence_type
        )

        current = best_by_type.get(
            evidence_type
        )

        if (
            current is None
            or candidate.score
            > current.score
        ):
            best_by_type[
                evidence_type
            ] = candidate

    return sorted(
        best_by_type.values(),
        key=lambda candidate: (
            candidate.page_number
            if candidate.page_number
            is not None
            else 9999,
            candidate.evidence_type,
        ),
    )


# ---------------------------------------------------------------------------
# BUILD MECHANISM EVIDENCE CANDIDATES
# ---------------------------------------------------------------------------
def build_mechanism_evidence_candidates(
    candidates: list[
        CharacterizationCandidate
    ],
) -> list[
    MechanismEvidenceCandidate
]:
    mechanism_evidence: list[
        MechanismEvidenceCandidate
    ] = []

    for candidate in candidates:
        include_candidate = (
            candidate.characterization_role
            == CharacterizationRole.MECHANISM_ASSESSMENT
        )

        if (
            candidate.characterization_role
            == CharacterizationRole.BAND_STRUCTURE
            and candidate.section_role
            == PaperSectionRole.MECHANISM
        ):
            include_candidate = True

        if not include_candidate:
            continue

        mechanism_evidence.append(
            MechanismEvidenceCandidate(
                evidence_type=(
                    candidate.evidence_type
                ),
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
                page_number=(
                    candidate.page_number
                ),
                section_title=(
                    candidate.section_title
                ),
                section_role=(
                    candidate.section_role
                ),
                matched_terms=(
                    candidate.matched_terms
                ),
                source_text=(
                    candidate.source_text
                ),
                score=candidate.score,
            )
        )

    return mechanism_evidence


# ---------------------------------------------------------------------------
# EXTRACT MECHANISM CLAIMS
# ---------------------------------------------------------------------------
def extract_mechanism_claims(
    passages: list[RelevantPassage],
) -> list[MechanismClaimCandidate]:
    raw_candidates = (
        extract_raw_mechanism_claims(
            passages
        )
    )

    return consolidate_mechanism_claims(
        raw_candidates
    )


# ---------------------------------------------------------------------------
# EXTRACT MECHANISM CANDIDATES
# ---------------------------------------------------------------------------
def extract_mechanism_candidates(
    passages: list[RelevantPassage],
) -> MechanismExtractionResult:
    mechanism_claims = (
        extract_mechanism_claims(
            passages
        )
    )

    raw_characterization_candidates = (
        extract_characterization_candidates(
            passages
        )
    )

    characterization_candidates = (
        consolidate_characterization_candidates(
            raw_characterization_candidates
        )
    )

    mechanism_evidence_candidates = (
        build_mechanism_evidence_candidates(
            characterization_candidates
        )
    )

    return MechanismExtractionResult(
        mechanism_claims=(
            mechanism_claims
        ),
        characterization_candidates=(
            characterization_candidates
        ),
        mechanism_evidence_candidates=(
            mechanism_evidence_candidates
        ),
    )


