import re

from dataclasses import (
    dataclass,
)


# ---------------------------------------------------------------------------
# MATERIAL SIGNAL RESULT
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MaterialSignalResult:
    has_perovskite_signal: bool

    has_tmd_signal: bool

    matched_perovskite_terms: tuple[
        str,
        ...
    ]

    matched_abo3_formulas: tuple[
        str,
        ...
    ]

    matched_known_perovskite_formulas: tuple[
        str,
        ...
    ]

    matched_tmd_terms: tuple[
        str,
        ...
    ]

    @property
    def matched_perovskite_formulas(
        self,
    ) -> tuple[
        str,
        ...
    ]:
        """
        Compatibility alias.

        Only known oxide-perovskite formulas are returned here.
        Generic ABO3-like matches must not be interpreted as
        confirmed perovskite structures.
        """
        return (
            self.matched_known_perovskite_formulas
        )


# ---------------------------------------------------------------------------
# PEROVSKITE TERMS
# ---------------------------------------------------------------------------
PEROVSKITE_TERMS = (
    "perovskite",
    "perovskites",
    "perovskite-type",
    "perovskite type",
    "perovskite-like",
    "perovskite like",
)


# ---------------------------------------------------------------------------
# KNOWN OXIDE PEROVSKITE FORMULAS
# ---------------------------------------------------------------------------
KNOWN_OXIDE_PEROVSKITE_FORMULAS = (
    "BaTiO3",
    "BiFeO3",
    "CaTiO3",
    "LaCoO3",
    "LaFeO3",
    "LaNiO3",
    "PbTiO3",
    "SrTiO3",
)


# ---------------------------------------------------------------------------
# TMD TERMS
# ---------------------------------------------------------------------------
TMD_TERMS = (
    "mos2",
    "ws2",
    "mose2",
    "wse2",
    "mote2",
    "wte2",
    "mosse",
    "wsse",
    "transition metal dichalcogenide",
    "transition metal dichalcogenides",
)


# ---------------------------------------------------------------------------
# ABO3-LIKE FORMULA PATTERN
# ---------------------------------------------------------------------------
ABO3_FORMULA_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"([A-Z][a-z]?"
    r"[A-Z][a-z]?"
    r"O3)"
    r"(?![A-Za-z0-9])"
)


# ---------------------------------------------------------------------------
# NORMALIZE MATERIAL TEXT
# ---------------------------------------------------------------------------
def normalize_material_text(
    value: str,
) -> str:
    normalized = (
        value
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
    normalized_text = (
        text.lower()
    )

    return tuple(
        term
        for term in terms
        if term in normalized_text
    )


# ---------------------------------------------------------------------------
# FIND ABO3-LIKE FORMULAS
# ---------------------------------------------------------------------------
def find_abo3_formulas(
    text: str,
) -> tuple[
    str,
    ...
]:
    matches = {
        match.group(
            1
        )
        for match in (
            ABO3_FORMULA_PATTERN
            .finditer(
                text
            )
        )
    }

    return tuple(
        sorted(
            matches
        )
    )


# ---------------------------------------------------------------------------
# FIND KNOWN PEROVSKITE FORMULAS
# ---------------------------------------------------------------------------
def find_known_perovskite_formulas(
    formulas: tuple[
        str,
        ...
    ],
) -> tuple[
    str,
    ...
]:
    known_formulas = set(
        KNOWN_OXIDE_PEROVSKITE_FORMULAS
    )

    return tuple(
        formula
        for formula in formulas
        if formula in known_formulas
    )


# ---------------------------------------------------------------------------
# DETECT MATERIAL SIGNALS
# ---------------------------------------------------------------------------
def detect_material_signals(
    value: str,
) -> MaterialSignalResult:
    text = (
        normalize_material_text(
            value
        )
    )

    matched_perovskite_terms = (
        find_matched_terms(
            text,
            PEROVSKITE_TERMS,
        )
    )

    matched_abo3_formulas = (
        find_abo3_formulas(
            text
        )
    )

    matched_known_perovskite_formulas = (
        find_known_perovskite_formulas(
            matched_abo3_formulas
        )
    )

    matched_tmd_terms = (
        find_matched_terms(
            text,
            TMD_TERMS,
        )
    )

    has_perovskite_signal = bool(
        matched_perovskite_terms
        or matched_abo3_formulas
    )

    has_tmd_signal = bool(
        matched_tmd_terms
    )

    return MaterialSignalResult(
        has_perovskite_signal=(
            has_perovskite_signal
        ),
        has_tmd_signal=(
            has_tmd_signal
        ),
        matched_perovskite_terms=(
            matched_perovskite_terms
        ),
        matched_abo3_formulas=(
            matched_abo3_formulas
        ),
        matched_known_perovskite_formulas=(
            matched_known_perovskite_formulas
        ),
        matched_tmd_terms=(
            matched_tmd_terms
        ),
    )

