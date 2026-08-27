import pytest

from psk_tmd.corpus.cardenas_reference import (
    build_cardenas_lookup,
)
from psk_tmd.corpus.compound_electronegativity import (
    calculate_compound_absolute_electronegativity,
)


# ---------------------------------------------------------------------------
# CALCULATE EXPECTED GEOMETRIC MEAN
# ---------------------------------------------------------------------------
def geometric_mean(
    values: list[
        tuple[
            float,
            float,
        ]
    ],
) -> float:
    numerator = 1.0
    denominator = 0.0

    for (
        value,
        coefficient,
    ) in values:
        numerator *= (
            value
            ** coefficient
        )

        denominator += (
            coefficient
        )

    return (
        numerator
        ** (
            1.0
            / denominator
        )
    )


# ---------------------------------------------------------------------------
# CALCIUM TITANATE
# ---------------------------------------------------------------------------
def test_catio3_electronegativity():
    lookup = (
        build_cardenas_lookup()
    )

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "Ca": 1.0,
                "Ti": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        geometric_mean(
            [
                (
                    3.07,
                    1.0,
                ),
                (
                    3.45,
                    1.0,
                ),
                (
                    7.54,
                    3.0,
                ),
            ]
        )
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# LANTHANUM NICKELATE
# ---------------------------------------------------------------------------
def test_lanio3_electronegativity():
    lookup = (
        build_cardenas_lookup()
    )

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "La": 1.0,
                "Ni": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        geometric_mean(
            [
                (
                    3.03,
                    1.0,
                ),
                (
                    4.40,
                    1.0,
                ),
                (
                    7.54,
                    3.0,
                ),
            ]
        )
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# LEAD TITANATE
# ---------------------------------------------------------------------------
def test_pbtio3_electronegativity():
    lookup = (
        build_cardenas_lookup()
    )

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "Pb": 1.0,
                "Ti": 1.0,
                "O": 3.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        geometric_mean(
            [
                (
                    3.88,
                    1.0,
                ),
                (
                    3.45,
                    1.0,
                ),
                (
                    7.54,
                    3.0,
                ),
            ]
        )
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# MOLYBDENUM DISULFIDE
# ---------------------------------------------------------------------------
def test_mos2_electronegativity():
    lookup = (
        build_cardenas_lookup()
    )

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "Mo": 1.0,
                "S": 2.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        geometric_mean(
            [
                (
                    3.92,
                    1.0,
                ),
                (
                    6.22,
                    2.0,
                ),
            ]
        )
    )

    assert result == pytest.approx(
        expected
    )


# ---------------------------------------------------------------------------
# TUNGSTEN DISULFIDE
# ---------------------------------------------------------------------------
def test_ws2_electronegativity():
    lookup = (
        build_cardenas_lookup()
    )

    result = (
        calculate_compound_absolute_electronegativity(
            composition={
                "W": 1.0,
                "S": 2.0,
            },
            elemental_lookup=lookup,
        )
    )

    expected = (
        geometric_mean(
            [
                (
                    4.35,
                    1.0,
                ),
                (
                    6.22,
                    2.0,
                ),
            ]
        )
    )

    assert result == pytest.approx(
        expected
    )

