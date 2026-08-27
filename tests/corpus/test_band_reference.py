import pytest

from psk_tmd.common.constants import (
    BandReferenceScale,
)
from psk_tmd.corpus.band_reference import (
    convert_potential_to_nhe,
    convert_vacuum_energy_to_nhe,
    get_ag_agcl_offset_v,
    normalize_reference_detail,
)


# ---------------------------------------------------------------------------
# NORMALIZE REFERENCE DETAIL
# ---------------------------------------------------------------------------
def test_normalize_reference_detail():
    assert (
        normalize_reference_detail(
            "Saturated KCl"
        )
        == "saturated_kcl"
    )

    assert (
        normalize_reference_detail(
            "3 M KCl"
        )
        == "3m_kcl"
    )

    assert (
        normalize_reference_detail(
            "1M KCl"
        )
        == "1m_kcl"
    )


# ---------------------------------------------------------------------------
# AG/AGCL DEFAULT OFFSET
# ---------------------------------------------------------------------------
def test_ag_agcl_default_offset():
    assert (
        get_ag_agcl_offset_v(
            None
        )
        == pytest.approx(
            0.197
        )
    )


# ---------------------------------------------------------------------------
# AG/AGCL EXPLICIT OFFSET
# ---------------------------------------------------------------------------
def test_ag_agcl_explicit_offset():
    assert (
        get_ag_agcl_offset_v(
            "3 M KCl"
        )
        == pytest.approx(
            0.210
        )
    )

    assert (
        get_ag_agcl_offset_v(
            "1 M KCl"
        )
        == pytest.approx(
            0.235
        )
    )


# ---------------------------------------------------------------------------
# NHE PASSES THROUGH
# ---------------------------------------------------------------------------
def test_nhe_passes_through():
    result = convert_potential_to_nhe(
        value=-0.50,
        reference_scale=(
            BandReferenceScale.NHE
        ),
    )

    assert result == pytest.approx(
        -0.50
    )


# ---------------------------------------------------------------------------
# SHE PASSES THROUGH
# ---------------------------------------------------------------------------
def test_she_passes_through():
    result = convert_potential_to_nhe(
        value=0.25,
        reference_scale=(
            BandReferenceScale.SHE
        ),
    )

    assert result == pytest.approx(
        0.25
    )


# ---------------------------------------------------------------------------
# AG/AGCL TO NHE
# ---------------------------------------------------------------------------
def test_ag_agcl_to_nhe():
    result = convert_potential_to_nhe(
        value=-0.50,
        reference_scale=(
            BandReferenceScale.AG_AGCL
        ),
        reference_detail=(
            "saturated KCl"
        ),
    )

    assert result == pytest.approx(
        -0.303
    )


# ---------------------------------------------------------------------------
# SCE TO NHE
# ---------------------------------------------------------------------------
def test_sce_to_nhe():
    result = convert_potential_to_nhe(
        value=-0.50,
        reference_scale=(
            BandReferenceScale.SCE
        ),
    )

    assert result == pytest.approx(
        -0.256
    )


# ---------------------------------------------------------------------------
# RHE TO NHE
# ---------------------------------------------------------------------------
def test_rhe_to_nhe():
    result = convert_potential_to_nhe(
        value=0.0,
        reference_scale=(
            BandReferenceScale.RHE
        ),
        ph=7.0,
    )

    assert result == pytest.approx(
        -0.4137
    )


# ---------------------------------------------------------------------------
# RHE REQUIRES PH
# ---------------------------------------------------------------------------
def test_rhe_requires_ph():
    with pytest.raises(
        ValueError,
        match="pH is required",
    ):
        convert_potential_to_nhe(
            value=0.0,
            reference_scale=(
                BandReferenceScale.RHE
            ),
        )


# ---------------------------------------------------------------------------
# UNKNOWN REFERENCE FAILS
# ---------------------------------------------------------------------------
def test_unknown_reference_fails():
    with pytest.raises(
        ValueError,
        match=(
            "Unsupported electrochemical "
            "reference scale"
        ),
    ):
        convert_potential_to_nhe(
            value=-0.50,
            reference_scale=(
                BandReferenceScale.UNKNOWN
            ),
        )


# ---------------------------------------------------------------------------
# UNKNOWN AG/AGCL DETAIL FAILS
# ---------------------------------------------------------------------------
def test_unknown_ag_agcl_detail_fails():
    with pytest.raises(
        ValueError,
        match=(
            "Unsupported Ag/AgCl "
            "reference detail"
        ),
    ):
        get_ag_agcl_offset_v(
            "mystery electrolyte"
        )


# ---------------------------------------------------------------------------
# VACUUM ENERGY TO NHE
# ---------------------------------------------------------------------------
def test_vacuum_energy_to_nhe():
    result = (
        convert_vacuum_energy_to_nhe(
            -4.44
        )
    )

    assert result == pytest.approx(
        0.0
    )

    result = (
        convert_vacuum_energy_to_nhe(
            -4.00
        )
    )

    assert result == pytest.approx(
        -0.44
    )

