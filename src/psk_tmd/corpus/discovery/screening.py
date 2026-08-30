from dataclasses import (
    dataclass,
)

from psk_tmd.corpus.discovery.material_signals import (
    detect_material_signals,
)
from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)


# ---------------------------------------------------------------------------
# SCREENING RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DiscoveryScreeningResult:
    discovery_id: str

    has_perovskite_signal: bool

    has_tmd_signal: bool

    has_photo_signal: bool

    passes_screen: bool

    matched_perovskite_terms: tuple[str, ...]

    matched_perovskite_formulas: tuple[str, ...]

    matched_tmd_terms: tuple[str, ...]

    matched_photo_terms: tuple[str, ...]


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

    material_text = " ".join(
        value
        for value in (
            record.title,
            record.abstract,
        )
        if value is not None
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

    has_photo_signal = bool(
        photo_matches
    )

    passes_screen = (
        material_signals
        .has_perovskite_signal
        and material_signals
        .has_tmd_signal
        and has_photo_signal
    )

    return DiscoveryScreeningResult(
        discovery_id=(
            record.discovery_id
        ),
        has_perovskite_signal=(
            material_signals
            .has_perovskite_signal
        ),
        has_tmd_signal=(
            material_signals
            .has_tmd_signal
        ),
        has_photo_signal=(
            has_photo_signal
        ),
        passes_screen=(
            passes_screen
        ),
        matched_perovskite_terms=(
            material_signals
            .matched_perovskite_terms
        ),
        matched_perovskite_formulas=(
            material_signals
            .matched_perovskite_formulas
        ),
        matched_tmd_terms=(
            material_signals
            .matched_tmd_terms
        ),
        matched_photo_terms=(
            photo_matches
        ),
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

