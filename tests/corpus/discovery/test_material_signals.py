from psk_tmd.corpus.discovery.material_signals import (
    detect_material_signals,
    find_abo3_formulas,
    find_known_perovskite_formulas,
    normalize_material_text,
)


# ---------------------------------------------------------------------------
# NORMALIZE MATERIAL TEXT
# ---------------------------------------------------------------------------
def test_normalize_material_text():
    result = normalize_material_text(
        "CaTiO₃ / MoS₂ — composite"
    )

    assert (
        result
        == "CaTiO3 / MoS2 - composite"
    )


# ---------------------------------------------------------------------------
# DETECT KNOWN PEROVSKITE AND TMD
# ---------------------------------------------------------------------------
def test_detect_known_perovskite_and_tmd():
    result = detect_material_signals(
        "CaTiO3/MoS2 heterostructure"
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

    assert (
        result.matched_tmd_terms
        == (
            "mos2",
        )
    )


# ---------------------------------------------------------------------------
# DETECT GENERIC PEROVSKITE TERM
# ---------------------------------------------------------------------------
def test_detect_generic_perovskite_term():
    result = detect_material_signals(
        (
            "Perovskite material "
            "coupled with WS2"
        )
    )

    assert (
        result.has_perovskite_signal
        is True
    )

    assert (
        "perovskite"
        in result.matched_perovskite_terms
    )

    assert (
        result.matched_known_perovskite_formulas
        == ()
    )

    assert (
        result.has_tmd_signal
        is True
    )


# ---------------------------------------------------------------------------
# DETECT UNICODE SUBSCRIPTS
# ---------------------------------------------------------------------------
def test_detect_unicode_subscripts():
    result = detect_material_signals(
        "LaCoO₃/MoS₂ photocatalyst"
    )

    assert (
        result.matched_abo3_formulas
        == (
            "LaCoO3",
        )
    )

    assert (
        result.matched_known_perovskite_formulas
        == (
            "LaCoO3",
        )
    )

    assert (
        result.matched_tmd_terms
        == (
            "mos2",
        )
    )


# ---------------------------------------------------------------------------
# FIND ABO3-LIKE FORMULA
# ---------------------------------------------------------------------------
def test_find_abo3_formula():
    formulas = find_abo3_formulas(
        "The sample contains SrTiO3."
    )

    assert formulas == (
        "SrTiO3",
    )


# ---------------------------------------------------------------------------
# UNKNOWN ABO3 IS NOT KNOWN PEROVSKITE
# ---------------------------------------------------------------------------
def test_unknown_abo3_is_not_known_perovskite():
    result = detect_material_signals(
        (
            "FeTiO3/MoS2 material "
            "for photocatalysis"
        )
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
# HCO3 IS ONLY ABO3-LIKE TEXT
# ---------------------------------------------------------------------------
def test_hco3_is_not_known_perovskite():
    result = detect_material_signals(
        (
            "HCO3 species were observed "
            "during MoS2 photocatalysis"
        )
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


# ---------------------------------------------------------------------------
# FIND KNOWN PEROVSKITE FORMULAS
# ---------------------------------------------------------------------------
def test_find_known_perovskite_formulas():
    result = (
        find_known_perovskite_formulas(
            (
                "CaTiO3",
                "FeTiO3",
                "HCO3",
            )
        )
    )

    assert result == (
        "CaTiO3",
    )


# ---------------------------------------------------------------------------
# MULTIPLE TMD TERMS
# ---------------------------------------------------------------------------
def test_multiple_tmd_terms():
    result = detect_material_signals(
        (
            "MoS2 and WS2 are transition "
            "metal dichalcogenides"
        )
    )

    assert (
        "mos2"
        in result.matched_tmd_terms
    )

    assert (
        "ws2"
        in result.matched_tmd_terms
    )

    assert (
        "transition metal dichalcogenide"
        in result.matched_tmd_terms
    )


# ---------------------------------------------------------------------------
# NO MATERIAL SIGNALS
# ---------------------------------------------------------------------------
def test_no_material_signals():
    result = detect_material_signals(
        "TiO2 photocatalyst"
    )

    assert (
        result.has_perovskite_signal
        is False
    )

    assert (
        result.has_tmd_signal
        is False
    )

    assert (
        result.matched_abo3_formulas
        == ()
    )

    assert (
        result.matched_known_perovskite_formulas
        == ()
    )


# ---------------------------------------------------------------------------
# COMPATIBILITY PROPERTY
# ---------------------------------------------------------------------------
def test_matched_perovskite_formulas_compatibility_property():
    result = detect_material_signals(
        "PbTiO3/MoS2 composite"
    )

    assert (
        result.matched_perovskite_formulas
        == result.matched_known_perovskite_formulas
    )

    assert (
        result.matched_perovskite_formulas
        == (
            "PbTiO3",
        )
    )

