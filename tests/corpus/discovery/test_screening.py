from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    build_screening_text,
    find_matched_terms,
    normalize_screening_text,
    screen_discovery_record,
)


# ---------------------------------------------------------------------------
# MAKE DISCOVERY RECORD
# ---------------------------------------------------------------------------
def make_record(
    *,
    title: str,
    abstract: str | None = None,
) -> DiscoveryRecord:
    return DiscoveryRecord(
        discovery_id="DSC-000001",
        title=title,
        abstract=abstract,
        source="test",
    )


# ---------------------------------------------------------------------------
# NORMALIZE SCREENING TEXT
# ---------------------------------------------------------------------------
def test_normalize_screening_text():
    result = normalize_screening_text(
        "MoS₂ / CaTiO₃ — "
        "Visible-Light Photocatalysis"
    )

    assert result == (
        "mos2 / catio3 - "
        "visible-light photocatalysis"
    )


# ---------------------------------------------------------------------------
# BUILD SCREENING TEXT
# ---------------------------------------------------------------------------
def test_build_screening_text_uses_title_and_abstract():
    record = make_record(
        title=(
            "CaTiO3/MoS2 "
            "heterostructure"
        ),
        abstract=(
            "Visible-light "
            "photocatalysis was studied."
        ),
    )

    text = build_screening_text(
        record
    )

    assert (
        "catio3/mos2"
        in text
    )

    assert (
        "photocatalysis"
        in text
    )


# ---------------------------------------------------------------------------
# FIND MATCHED TERMS
# ---------------------------------------------------------------------------
def test_find_matched_terms():
    matches = find_matched_terms(
        (
            "mos2 photocatalytic "
            "heterostructure"
        ),
        (
            "mos2",
            "ws2",
            "photocatalytic",
        ),
    )

    assert matches == (
        "mos2",
        "photocatalytic",
    )


# ---------------------------------------------------------------------------
# EXPLICIT PEROVSKITE TARGET PASSES
# ---------------------------------------------------------------------------
def test_explicit_perovskite_target_passes():
    record = make_record(
        title=(
            "Perovskite CaTiO3/MoS2 "
            "heterostructure for "
            "photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.has_tmd_signal
        is True
    )

    assert (
        result.has_photo_signal
        is True
    )

    assert (
        result.passes_screen
        is True
    )


# ---------------------------------------------------------------------------
# FORMULA-ONLY PEROVSKITE SIGNAL PASSES
# ---------------------------------------------------------------------------
def test_formula_only_perovskite_signal_passes():
    record = make_record(
        title=(
            "CaTiO3/MoS2 "
            "heterojunction for "
            "photocatalytic hydrogen "
            "production"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.matched_perovskite_formulas
        == (
            "CaTiO3",
        )
    )

    assert (
        result.has_tmd_signal
        is True
    )

    assert (
        result.has_photo_signal
        is True
    )

    assert (
        result.passes_screen
        is True
    )


# ---------------------------------------------------------------------------
# LACO3 FORMULA TARGET PASSES
# ---------------------------------------------------------------------------
def test_laco3_formula_target_passes():
    record = make_record(
        title=(
            "LaCoO3/MoS2 "
            "heterostructure for "
            "visible-light photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.matched_perovskite_formulas
        == (
            "LaCoO3",
        )
    )

    assert (
        result.passes_screen
        is True
    )


# ---------------------------------------------------------------------------
# ABSTRACT CAN SUPPLY PHOTO SIGNAL
# ---------------------------------------------------------------------------
def test_abstract_can_supply_photo_signal():
    record = make_record(
        title=(
            "CaTiO3/MoS2 "
            "heterostructure"
        ),
        abstract=(
            "The composite showed "
            "visible-light photocatalytic "
            "activity."
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.passes_screen
        is True
    )


# ---------------------------------------------------------------------------
# SOLAR CELL RECORD FAILS
# ---------------------------------------------------------------------------
def test_solar_cell_record_fails():
    record = make_record(
        title=(
            "Two-dimensional MoS2 "
            "materials in perovskite "
            "solar cells"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.has_tmd_signal
        is True
    )

    assert (
        result.has_photo_signal
        is False
    )

    assert (
        result.passes_screen
        is False
    )


# ---------------------------------------------------------------------------
# NON-TMD PHOTOCATALYST FAILS
# ---------------------------------------------------------------------------
def test_non_tmd_photocatalyst_fails():
    record = make_record(
        title=(
            "CaTiO3 photocatalyst "
            "for hydrogen production"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.has_tmd_signal
        is False
    )

    assert (
        result.passes_screen
        is False
    )


# ---------------------------------------------------------------------------
# NON-PEROVSKITE MOS2 FAILS
# ---------------------------------------------------------------------------
def test_non_perovskite_mos2_fails():
    record = make_record(
        title=(
            "MoS2/g-C3N4 composite "
            "for photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.has_perovskite_signal
        is False
    )

    assert (
        result.has_tmd_signal
        is True
    )

    assert (
        result.has_photo_signal
        is True
    )

    assert (
        result.passes_screen
        is False
    )


