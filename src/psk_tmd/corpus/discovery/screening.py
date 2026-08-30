from dataclasses import (
    dataclass,
)
from enum import (
    Enum,
)

from psk_tmd.corpus.discovery.material_signals import (
    detect_material_signals,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)


# ---------------------------------------------------------------------------
# SCREENING STATUS
# ---------------------------------------------------------------------------
class DiscoveryScreeningStatus(
    str,
    Enum,
):
    PASS = "pass"
    REVIEW = "review"
    REJECT = "reject"


# ---------------------------------------------------------------------------
# SCREENING RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryScreeningResult:
    discovery_id: str

    status: DiscoveryScreeningStatus

    has_perovskite_signal: bool

    has_oxide_perovskite_signal: bool

    has_halide_perovskite_signal: bool

    has_tmd_signal: bool

    has_photo_signal: bool

    matched_perovskite_terms: tuple[str, ...]

    matched_perovskite_formulas: tuple[str, ...]

    matched_oxide_perovskite_terms: tuple[str, ...]

    matched_halide_perovskite_terms: tuple[str, ...]

    matched_halide_perovskite_formulas: tuple[str, ...]

    matched_tmd_terms: tuple[str, ...]

    matched_photo_terms: tuple[str, ...]

    reason: str

    @property
    def passes_screen(
        self,
    ) -> bool:
        return (
            self.status
            == DiscoveryScreeningStatus.PASS
        )


# ---------------------------------------------------------------------------
# PHOTO TERMS
# ---------------------------------------------------------------------------
PHOTO_TERMS = (
    "photocatalysis",
    "photocatalytic",
    "photocatalyst",
    "photocatalysts",
    "photo-assisted",
    "photoassisted",
    "photoelectrocatalysis",
    "photoelectrocatalytic",
    "photoelectrochemical",
    "visible-light",
    "visible light",
    "solar-driven",
    "solar driven",
    "light-driven",
    "light driven",
)


# ---------------------------------------------------------------------------
# OXIDE PEROVSKITE TERMS
# ---------------------------------------------------------------------------
OXIDE_PEROVSKITE_TERMS = (
    "perovskite oxide",
    "perovskite oxides",
    "oxide perovskite",
    "oxide perovskites",
    "oxide-perovskite",
    "oxide-perovskites",
)


# ---------------------------------------------------------------------------
# HALIDE PEROVSKITE TERMS
# ---------------------------------------------------------------------------
HALIDE_PEROVSKITE_TERMS = (
    "halide perovskite",
    "halide perovskites",
    "metal halide perovskite",
    "metal halide perovskites",
    "lead halide perovskite",
    "lead halide perovskites",
)


# ---------------------------------------------------------------------------
# HALIDE PEROVSKITE FORMULAS
# ---------------------------------------------------------------------------
HALIDE_PEROVSKITE_FORMULAS = (
    "CsPbBr3",
    "CsPbI3",
    "CsPbCl3",
    "MAPbI3",
    "MAPbBr3",
    "MAPbCl3",
    "FAPbI3",
    "FAPbBr3",
    "FAPbCl3",
    "CH3NH3PbI3",
    "CH3NH3PbBr3",
    "CH3NH3PbCl3",
)


# ---------------------------------------------------------------------------
# NORMALIZE SCREENING TEXT
# ---------------------------------------------------------------------------
def normalize_screening_text(
    value: str,
) -> str:
    normalized = (
        value
        .lower()
        .replace(
            "₂",
            "2",
        )
        .replace(
            "₃",
            "3",
        )
        .replace(
            "–",
            "-",
        )
        .replace(
            "—",
            "-",
        )
    )

    return " ".join(
        normalized.split()
    )


# ---------------------------------------------------------------------------
# BUILD SCREENING TEXT
# ---------------------------------------------------------------------------
def build_screening_text(
    record: DiscoveryRecord,
) -> str:
    values = [
        record.title,
        record.abstract,
    ]

    return normalize_screening_text(
        " ".join(
            value
            for value in values
            if value is not None
        )
    )


# ---------------------------------------------------------------------------
# BUILD MATERIAL TEXT
# ---------------------------------------------------------------------------
def build_material_text(
    record: DiscoveryRecord,
) -> str:
    return " ".join(
        value
        for value in (
            record.title,
            record.abstract,
        )
        if value is not None
    )


# ---------------------------------------------------------------------------
# FIND MATCHED TERMS
# ---------------------------------------------------------------------------
def find_matched_terms(
    text: str,
    terms: tuple[
        str,
        ...
    ],
) -> tuple[
    str,
    ...
]:
    matches = [
        term
        for term in terms
        if term in text
    ]

    return tuple(
        matches
    )


# ---------------------------------------------------------------------------
# FIND CASE-SENSITIVE FORMULAS
# ---------------------------------------------------------------------------
def find_case_sensitive_formulas(
    text: str,
    formulas: tuple[
        str,
        ...
    ],
) -> tuple[
    str,
    ...
]:
    matches = [
        formula
        for formula in formulas
        if formula in text
    ]

    return tuple(
        matches
    )


# ---------------------------------------------------------------------------
# RESOLVE SCREENING STATUS
# ---------------------------------------------------------------------------
def resolve_screening_status(
    *,
    has_perovskite_signal: bool,
    has_oxide_perovskite_signal: bool,
    has_halide_perovskite_signal: bool,
    has_tmd_signal: bool,
    has_photo_signal: bool,
) -> tuple[
    DiscoveryScreeningStatus,
    str,
]:
    if not has_tmd_signal:
        return (
            DiscoveryScreeningStatus.REJECT,
            "No TMD signal was detected.",
        )

    if not has_photo_signal:
        return (
            DiscoveryScreeningStatus.REJECT,
            "No photocatalytic or photo-assisted signal was detected.",
        )

    if (
        has_oxide_perovskite_signal
        and has_halide_perovskite_signal
    ):
        return (
            DiscoveryScreeningStatus.REVIEW,
            (
                "Both oxide-perovskite and halide-perovskite "
                "signals were detected."
            ),
        )

    if has_oxide_perovskite_signal:
        return (
            DiscoveryScreeningStatus.PASS,
            "Explicit oxide-perovskite evidence was detected.",
        )

    if has_halide_perovskite_signal:
        return (
            DiscoveryScreeningStatus.REJECT,
            (
                "Halide-perovskite evidence was detected without "
                "oxide-perovskite evidence."
            ),
        )

    if has_perovskite_signal:
        return (
            DiscoveryScreeningStatus.REVIEW,
            (
                "Generic perovskite evidence was detected, but oxide "
                "identity could not be established from metadata."
            ),
        )

    return (
        DiscoveryScreeningStatus.REJECT,
        "No perovskite signal was detected.",
    )


# ---------------------------------------------------------------------------
# SCREEN DISCOVERY RECORD
# ---------------------------------------------------------------------------
def screen_discovery_record(
    record: DiscoveryRecord,
) -> DiscoveryScreeningResult:
    screening_text = (
        build_screening_text(
            record
        )
    )

    material_text = (
        build_material_text(
            record
        )
    )

    material_signals = (
        detect_material_signals(
            material_text
        )
    )

    photo_matches = (
        find_matched_terms(
            screening_text,
            PHOTO_TERMS,
        )
    )

    oxide_term_matches = (
        find_matched_terms(
            screening_text,
            OXIDE_PEROVSKITE_TERMS,
        )
    )

    halide_term_matches = (
        find_matched_terms(
            screening_text,
            HALIDE_PEROVSKITE_TERMS,
        )
    )

    halide_formula_matches = (
        find_case_sensitive_formulas(
            material_text,
            HALIDE_PEROVSKITE_FORMULAS,
        )
    )

    has_photo_signal = bool(
        photo_matches
    )

    has_oxide_perovskite_signal = bool(
        material_signals
        .matched_perovskite_formulas
        or oxide_term_matches
    )

    has_halide_perovskite_signal = bool(
        halide_term_matches
        or halide_formula_matches
    )

    status, reason = (
        resolve_screening_status(
            has_perovskite_signal=(
                material_signals
                .has_perovskite_signal
            ),
            has_oxide_perovskite_signal=(
                has_oxide_perovskite_signal
            ),
            has_halide_perovskite_signal=(
                has_halide_perovskite_signal
            ),
            has_tmd_signal=(
                material_signals
                .has_tmd_signal
            ),
            has_photo_signal=(
                has_photo_signal
            ),
        )
    )

    return DiscoveryScreeningResult(
        discovery_id=(
            record.discovery_id
        ),
        status=status,
        has_perovskite_signal=(
            material_signals
            .has_perovskite_signal
        ),
        has_oxide_perovskite_signal=(
            has_oxide_perovskite_signal
        ),
        has_halide_perovskite_signal=(
            has_halide_perovskite_signal
        ),
        has_tmd_signal=(
            material_signals
            .has_tmd_signal
        ),
        has_photo_signal=(
            has_photo_signal
        ),
        matched_perovskite_terms=(
            material_signals
            .matched_perovskite_terms
        ),
        matched_perovskite_formulas=(
            material_signals
            .matched_perovskite_formulas
        ),
        matched_oxide_perovskite_terms=(
            oxide_term_matches
        ),
        matched_halide_perovskite_terms=(
            halide_term_matches
        ),
        matched_halide_perovskite_formulas=(
            halide_formula_matches
        ),
        matched_tmd_terms=(
            material_signals
            .matched_tmd_terms
        ),
        matched_photo_terms=(
            photo_matches
        ),
        reason=reason,
    )


# ---------------------------------------------------------------------------
# SCREEN DISCOVERY RECORDS
# ---------------------------------------------------------------------------
def screen_discovery_records(
    records: list[
        DiscoveryRecord
    ],
) -> list[
    DiscoveryScreeningResult
]:
    return [
        screen_discovery_record(
            record
        )
        for record in records
    ]


