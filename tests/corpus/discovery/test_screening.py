from psk_tmd.corpus.discovery.models import (
    DiscoveryRecord,
)
from psk_tmd.corpus.discovery.screening import (
    DiscoveryScreeningStatus,
    build_material_text,
    build_screening_text,
    find_case_sensitive_formulas,
    find_matched_terms,
    normalize_screening_text,
    resolve_screening_status,
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
# BUILD MATERIAL TEXT PRESERVES FORMULA CASE
# ---------------------------------------------------------------------------
def test_build_material_text_preserves_formula_case():
    record = make_record(
        title=(
            "CaTiO3/MoS2 "
            "heterostructure"
        ),
    )

    text = build_material_text(
        record
    )

    assert (
        "CaTiO3/MoS2"
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
# FIND HALIDE FORMULA
# ---------------------------------------------------------------------------
def test_find_case_sensitive_halide_formula():
    matches = (
        find_case_sensitive_formulas(
            "CsPbBr3-MoS2 photocatalyst",
            (
                "CsPbBr3",
                "MAPbI3",
            ),
        )
    )

    assert matches == (
        "CsPbBr3",
    )


# ---------------------------------------------------------------------------
# OXIDE FORMULA TARGET PASSES
# ---------------------------------------------------------------------------
def test_oxide_formula_target_passes():
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
        result.status
        == DiscoveryScreeningStatus.PASS
    )

    assert (
        result.has_oxide_perovskite_signal
        is True
    )

    assert (
        result.has_halide_perovskite_signal
        is False
    )

    assert (
        result.passes_screen
        is True
    )


# ---------------------------------------------------------------------------
# EXPLICIT OXIDE PEROVSKITE TARGET PASSES
# ---------------------------------------------------------------------------
def test_explicit_oxide_perovskite_target_passes():
    record = make_record(
        title=(
            "Perovskite oxide/MoS2 "
            "heterostructure for "
            "photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.PASS
    )

    assert (
        result.has_oxide_perovskite_signal
        is True
    )


# ---------------------------------------------------------------------------
# LACO3 TARGET PASSES
# ---------------------------------------------------------------------------
def test_laco3_target_passes():
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
        result.status
        == DiscoveryScreeningStatus.PASS
    )

    assert (
        result.matched_perovskite_formulas
        == (
            "LaCoO3",
        )
    )


# ---------------------------------------------------------------------------
# GENERIC PEROVSKITE TARGET NEEDS REVIEW
# ---------------------------------------------------------------------------
def test_generic_perovskite_target_needs_review():
    record = make_record(
        title=(
            "Perovskite/MoS2 "
            "heterostructure for "
            "photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.REVIEW
    )

    assert (
        result.passes_screen
        is False
    )


# ---------------------------------------------------------------------------
# HALIDE PEROVSKITE TERM REJECTED
# ---------------------------------------------------------------------------
def test_halide_perovskite_term_rejected():
    record = make_record(
        title=(
            "Metal halide perovskite "
            "coupled with MoS2 for "
            "photocatalytic degradation"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.REJECT
    )

    assert (
        result.has_halide_perovskite_signal
        is True
    )


# ---------------------------------------------------------------------------
# CSPBBR3 HALIDE FORMULA REJECTED
# ---------------------------------------------------------------------------
def test_cspbbr3_halide_formula_rejected():
    record = make_record(
        title=(
            "CsPbBr3 perovskite "
            "nanocrystals anchored on "
            "MoS2 for photocatalytic "
            "degradation"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.REJECT
    )

    assert (
        result.matched_halide_perovskite_formulas
        == (
            "CsPbBr3",
        )
    )


# ---------------------------------------------------------------------------
# CONFLICTING OXIDE AND HALIDE SIGNALS NEED REVIEW
# ---------------------------------------------------------------------------
def test_conflicting_perovskite_signals_need_review():
    record = make_record(
        title=(
            "CaTiO3 and CsPbBr3 "
            "perovskites coupled with "
            "MoS2 for photocatalysis"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.REVIEW
    )

    assert (
        result.has_oxide_perovskite_signal
        is True
    )

    assert (
        result.has_halide_perovskite_signal
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
        result.status
        == DiscoveryScreeningStatus.PASS
    )


# ---------------------------------------------------------------------------
# SOLAR CELL RECORD REJECTED
# ---------------------------------------------------------------------------
def test_solar_cell_record_rejected():
    record = make_record(
        title=(
            "CaTiO3/MoS2 materials "
            "for solar cells"
        ),
    )

    result = screen_discovery_record(
        record
    )

    assert (
        result.status
        == DiscoveryScreeningStatus.REJECT
    )

    assert (
        result.has_photo_signal
        is False
    )


# ---------------------------------------------------------------------------
# NON-TMD PHOTOCATALYST REJECTED
# ---------------------------------------------------------------------------
def test_non_tmd_photocatalyst_rejected():
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
        result.status
        == DiscoveryScreeningStatus.REJECT
    )

    assert (
        result.has_tmd_signal
        is False
    )


# ---------------------------------------------------------------------------
# NON-PEROVSKITE MOS2 REJECTED
# ---------------------------------------------------------------------------
def test_non_perovskite_mos2_rejected():
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
        result.status
        == DiscoveryScreeningStatus.REJECT
    )

    assert (
        result.has_perovskite_signal
        is False
    )


# ---------------------------------------------------------------------------
# RESOLVE NO TMD
# ---------------------------------------------------------------------------
def test_resolve_screening_status_no_tmd():
    status, _ = resolve_screening_status(
        has_perovskite_signal=True,
        has_oxide_perovskite_signal=True,
        has_halide_perovskite_signal=False,
        has_tmd_signal=False,
        has_photo_signal=True,
    )

    assert (
        status
        == DiscoveryScreeningStatus.REJECT
    )


# ---------------------------------------------------------------------------
# RESOLVE GENERIC PEROVSKITE
# ---------------------------------------------------------------------------
def test_resolve_screening_status_generic_perovskite():
    status, _ = resolve_screening_status(
        has_perovskite_signal=True,
        has_oxide_perovskite_signal=False,
        has_halide_perovskite_signal=False,
        has_tmd_signal=True,
        has_photo_signal=True,
    )

    assert (
        status
        == DiscoveryScreeningStatus.REVIEW
    )


