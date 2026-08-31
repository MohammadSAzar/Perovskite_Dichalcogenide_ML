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
        (
            "MoS₂ / CaTiO₃ — "
            "Visible-Light Photocatalysis"
        )
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
# KNOWN OXIDE FORMULA PASSES
# ---------------------------------------------------------------------------
def test_known_oxide_formula_passes():
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
        result.matched_abo3_formulas
        == (
            "CaTiO3",
        )
    )

    assert (
        result.matched_known_perovskite_formulas
        == (
            "CaTiO3",
        )
    )


# ---------------------------------------------------------------------------
# EXPLICIT OXIDE PEROVSKITE PASSES
# ---------------------------------------------------------------------------
def test_explicit_oxide_perovskite_passes():
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
# UNKNOWN ABO3 NEEDS REVIEW
# ---------------------------------------------------------------------------
def test_unknown_abo3_needs_review():
    record = make_record(
        title=(
            "FeTiO3/MoS2 "
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
        result.matched_abo3_formulas
        == (
            "FeTiO3",
        )
    )

    assert (
        result.matched_known_perovskite_formulas
        == ()
    )


# ---------------------------------------------------------------------------
# HCO3 DOES NOT CREATE PASS
# ---------------------------------------------------------------------------
def test_hco3_does_not_create_pass():
    record = make_record(
        title=(
            "HCO3 and MoS2 during "
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
        result.matched_abo3_formulas
        == (
            "HCO3",
        )
    )

    assert (
        result.matched_known_perovskite_formulas
        == ()
    )

    assert (
        result.has_oxide_perovskite_signal
        is False
    )


# ---------------------------------------------------------------------------
# GENERIC PEROVSKITE NEEDS REVIEW
# ---------------------------------------------------------------------------
def test_generic_perovskite_needs_review():
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
# CSPBBR3 REJECTED
# ---------------------------------------------------------------------------
def test_cspbbr3_rejected():
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
# CONFLICTING SIGNALS NEED REVIEW
# ---------------------------------------------------------------------------
def test_conflicting_signals_need_review():
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
# NO PHOTO SIGNAL REJECTED
# ---------------------------------------------------------------------------
def test_no_photo_signal_rejected():
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
# NO TMD REJECTED
# ---------------------------------------------------------------------------
def test_no_tmd_rejected():
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


# ---------------------------------------------------------------------------
# NO PEROVSKITE REJECTED
# ---------------------------------------------------------------------------
def test_no_perovskite_rejected():
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


# ---------------------------------------------------------------------------
# RESOLVE UNKNOWN ABO3
# ---------------------------------------------------------------------------
def test_resolve_unknown_abo3():
    status, _ = resolve_screening_status(
        has_perovskite_signal=True,
        has_oxide_perovskite_signal=False,
        has_halide_perovskite_signal=False,
        has_abo3_signal=True,
        has_tmd_signal=True,
        has_photo_signal=True,
    )

    assert (
        status
        == DiscoveryScreeningStatus.REVIEW
    )


# ---------------------------------------------------------------------------
# RESOLVE KNOWN OXIDE
# ---------------------------------------------------------------------------
def test_resolve_known_oxide():
    status, _ = resolve_screening_status(
        has_perovskite_signal=True,
        has_oxide_perovskite_signal=True,
        has_halide_perovskite_signal=False,
        has_abo3_signal=True,
        has_tmd_signal=True,
        has_photo_signal=True,
    )

    assert (
        status
        == DiscoveryScreeningStatus.PASS
    )

