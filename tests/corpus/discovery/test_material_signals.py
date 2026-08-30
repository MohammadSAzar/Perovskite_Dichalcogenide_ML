from psk_tmd.corpus.discovery.material_signals import (
    detect_material_signals,
    find_oxide_perovskite_formulas,
    normalize_material_text,
)


# ---------------------------------------------------------------------------
# NORMALIZE MATERIAL TEXT
# ---------------------------------------------------------------------------
def test_normalize_material_text():
    result = normalize_material_text(
        "CaTiO₃/MoS₂"
    )

    assert result == (
        "CaTiO3/MoS2"
    )


# ---------------------------------------------------------------------------
# FIND SIMPLE OXIDE PEROVSKITE FORMULA
# ---------------------------------------------------------------------------
def test_find_simple_oxide_perovskite_formula():
    result = (
        find_oxide_perovskite_formulas(
            "CaTiO3/MoS2 "
            "heterostructure"
        )
    )

    assert result == (
        "CaTiO3",
    )


# ---------------------------------------------------------------------------
# FIND LANTHANUM OXIDE FORMULA
# ---------------------------------------------------------------------------
def test_find_lanthanum_oxide_formula():
    result = (
        find_oxide_perovskite_formulas(
            "LaCoO3 coupled with MoS2"
        )
    )

    assert result == (
        "LaCoO3",
    )


# ---------------------------------------------------------------------------
# EXPLICIT PEROVSKITE TERM
# ---------------------------------------------------------------------------
def test_explicit_perovskite_term():
    result = (
        detect_material_signals(
            "Perovskite oxide coupled "
            "with MoS2"
        )
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
        "perovskite"
        in result.matched_perovskite_terms
    )


# ---------------------------------------------------------------------------
# FORMULA PROVIDES PEROVSKITE SIGNAL
# ---------------------------------------------------------------------------
def test_formula_provides_perovskite_signal():
    result = (
        detect_material_signals(
            "CaTiO3/MoS2 heterojunction"
        )
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
        result.matched_perovskite_formulas
        == (
            "CaTiO3",
        )
    )


# ---------------------------------------------------------------------------
# PBSKITE TMD SUBSCRIPT NORMALIZATION
# ---------------------------------------------------------------------------
def test_subscript_formula_detection():
    result = (
        detect_material_signals(
            "PbTiO₃/MoS₂ photocatalyst"
        )
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.has_tmd_signal
        is True
    )


# ---------------------------------------------------------------------------
# TMD WITHOUT PEROVSKITE FAILS MATERIAL PAIR
# ---------------------------------------------------------------------------
def test_tmd_without_perovskite():
    result = (
        detect_material_signals(
            "MoS2/g-C3N4 photocatalyst"
        )
    )

    assert (
        result.has_perovskite_signal
        is False
    )

    assert (
        result.has_tmd_signal
        is True
    )


# ---------------------------------------------------------------------------
# PEROVSKITE WITHOUT TMD
# ---------------------------------------------------------------------------
def test_perovskite_without_tmd():
    result = (
        detect_material_signals(
            "CaTiO3 photocatalyst"
        )
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        result.has_tmd_signal
        is False
    )

