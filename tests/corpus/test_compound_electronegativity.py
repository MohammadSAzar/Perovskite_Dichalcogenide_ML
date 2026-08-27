import pytest

from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)
from psk_tmd.corpus.compound_electronegativity import (
    build_psk_anion_doped_composition,
    build_tmd_anion_doped_composition,
    calculate_compound_absolute_electronegativity,
    validate_composition,
)


# ---------------------------------------------------------------------------
# BUILD TEST RECORD
# ---------------------------------------------------------------------------
def make_record(
    symbol: str,
    value: float | None,
) -> ElementElectronegativityRecord:
    return (
        ElementElectronegativityRecord(
            element_symbol=symbol,
            chemical_potential_ev=(
                -value
                if value is not None
                else None
            ),
            absolute_electronegativity_ev=(
                value
            ),
            value_status=(
                ElectronegativityValueStatus
                .TABULATED
                if value is not None
                else
                ElectronegativityValueStatus
                .UNAVAILABLE
            ),
        )
    )


# ---------------------------------------------------------------------------
# SIMPLE TWO-ELEMENT COMPOSITION
# ---------------------------------------------------------------------------
def test_simple_two_element_composition():
    lookup = {
        "A": make_record(
            "A",
            4.0,
        ),
        "B": make_record(
            "B",
            9.0,
        ),
    }

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "A": 1.0,
                "B": 1.0,
            },
            elemental_lookup=lookup,
        )
    )

    assert result == pytest.approx(
        6.0
    )


# ---------------------------------------------------------------------------
# ABO3 COMPOSITION
# ---------------------------------------------------------------------------
def test_abo3_composition():
    lookup = {
        "A": make_record(
            "A",
            4.0,
        ),
        "B": make_record(
            "B",
            5.0,
        ),
        "O": make_record(
            "O",
            8.0,
        ),
    }

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "A": 1.0,
                "B": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        4.0
        * 5.0
        * 8.0**3
    ) ** (
        1.0 / 5.0
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# MX2 COMPOSITION
# ---------------------------------------------------------------------------
def test_mx2_composition():
    lookup = {
        "M": make_record(
            "M",
            4.0,
        ),
        "X": make_record(
            "X",
            9.0,
        ),
    }

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "M": 1.0,
                "X": 2.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        4.0
        * 9.0**2
    ) ** (
        1.0 / 3.0
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# FRACTIONAL STOICHIOMETRY
# ---------------------------------------------------------------------------
def test_fractional_stoichiometry():
    lookup = {
        "A": make_record(
            "A",
            4.0,
        ),
        "D": make_record(
            "D",
            9.0,
        ),
        "B": make_record(
            "B",
            5.0,
        ),
        "O": make_record(
            "O",
            8.0,
        ),
    }

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "A": 0.8,
                "D": 0.2,
                "B": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        4.0**0.8
        * 9.0**0.2
        * 5.0
        * 8.0**3
    ) ** (
        1.0 / 5.0
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# EMPTY COMPOSITION FAILS
# ---------------------------------------------------------------------------
def test_empty_composition_fails():
    with pytest.raises(
        ValueError,
        match=(
            "at least one element"
        ),
    ):
        validate_composition(
            {}
        )


# ---------------------------------------------------------------------------
# NONPOSITIVE COEFFICIENT FAILS
# ---------------------------------------------------------------------------
def test_nonpositive_coefficient_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be positive"
        ),
    ):
        validate_composition(
            {
                "Ti": 0.0,
            }
        )


# ---------------------------------------------------------------------------
# MISSING ELEMENT FAILS
# ---------------------------------------------------------------------------
def test_missing_element_fails():
    lookup = {
        "Ti": make_record(
            "Ti",
            3.45,
        ),
    }

    with pytest.raises(
        ValueError,
        match=(
            "No elemental "
            "electronegativity record"
        ),
    ):
        calculate_compound_absolute_electronegativity(
            composition={
                "Ti": 1.0,
                "O": 2.0,
            },
            elemental_lookup=lookup,
        )


# ---------------------------------------------------------------------------
# UNAVAILABLE ELECTRONEGATIVITY FAILS
# ---------------------------------------------------------------------------
def test_unavailable_electronegativity_fails():
    lookup = {
        "Pr": make_record(
            "Pr",
            None,
        ),
    }

    with pytest.raises(
        ValueError,
        match=(
            "is unavailable"
        ),
    ):
        calculate_compound_absolute_electronegativity(
            composition={
                "Pr": 1.0,
            },
            elemental_lookup=lookup,
        )


# ---------------------------------------------------------------------------
# PSK ANION DOPING
# ---------------------------------------------------------------------------
def test_psk_anion_doping():
    composition = (
        build_psk_anion_doped_composition(
            cation_composition={
                "La": 1.0,
                "Fe": 1.0,
            },
            anion_dopants={
                "N": 0.3,
            },
        )
    )

    assert composition == {
        "La": 1.0,
        "Fe": 1.0,
        "O": pytest.approx(
            2.7
        ),
        "N": pytest.approx(
            0.3
        ),
    }


# ---------------------------------------------------------------------------
# PSK CATION AND ANION DOPING
# ---------------------------------------------------------------------------
def test_psk_cation_and_anion_doping():
    composition = (
        build_psk_anion_doped_composition(
            cation_composition={
                "La": 0.8,
                "Sr": 0.2,
                "Fe": 1.0,
            },
            anion_dopants={
                "N": 0.2,
            },
        )
    )

    assert composition == {
        "La": pytest.approx(
            0.8
        ),
        "Sr": pytest.approx(
            0.2
        ),
        "Fe": 1.0,
        "O": pytest.approx(
            2.8
        ),
        "N": pytest.approx(
            0.2
        ),
    }


# ---------------------------------------------------------------------------
# TMD ANION DOPING
# ---------------------------------------------------------------------------
def test_tmd_anion_doping():
    composition = (
        build_tmd_anion_doped_composition(
            metal_composition={
                "Mo": 1.0,
            },
            host_chalcogen_symbol="S",
            anion_dopants={
                "Se": 0.5,
            },
        )
    )

    assert composition == {
        "Mo": 1.0,
        "S": pytest.approx(
            1.5
        ),
        "Se": pytest.approx(
            0.5
        ),
    }


# ---------------------------------------------------------------------------
# TMD METAL AND ANION DOPING
# ---------------------------------------------------------------------------
def test_tmd_metal_and_anion_doping():
    composition = (
        build_tmd_anion_doped_composition(
            metal_composition={
                "Mo": 0.8,
                "W": 0.2,
            },
            host_chalcogen_symbol="S",
            anion_dopants={
                "Se": 0.4,
            },
        )
    )

    assert composition == {
        "Mo": pytest.approx(
            0.8
        ),
        "W": pytest.approx(
            0.2
        ),
        "S": pytest.approx(
            1.6
        ),
        "Se": pytest.approx(
            0.4
        ),
    }


# ---------------------------------------------------------------------------
# MULTIPLE ANION DOPANTS
# ---------------------------------------------------------------------------
def test_multiple_anion_dopants():
    composition = (
        build_psk_anion_doped_composition(
            cation_composition={
                "La": 1.0,
                "Fe": 1.0,
            },
            anion_dopants={
                "N": 0.2,
                "F": 0.1,
            },
        )
    )

    assert composition == {
        "La": 1.0,
        "Fe": 1.0,
        "O": pytest.approx(
            2.7
        ),
        "N": pytest.approx(
            0.2
        ),
        "F": pytest.approx(
            0.1
        ),
    }


# ---------------------------------------------------------------------------
# EXCESS ANION DOPING FAILS
# ---------------------------------------------------------------------------
def test_excess_anion_doping_fails():
    with pytest.raises(
        ValueError,
        match=(
            "cannot exceed"
        ),
    ):
        build_tmd_anion_doped_composition(
            metal_composition={
                "Mo": 1.0,
            },
            host_chalcogen_symbol="S",
            anion_dopants={
                "Se": 2.1,
            },
        )

