import pytest

from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.corpus.cardenas_reference import (
    CARDENAS_NEUTRAL_CHEMICAL_POTENTIAL_EV,
    CARDENAS_SOURCE_NAME,
    CARDENAS_SOURCE_REFERENCE,
    build_cardenas_element_record,
    build_cardenas_lookup,
    build_cardenas_reference,
)


# ---------------------------------------------------------------------------
# CARDENAS REFERENCE SIZE
# ---------------------------------------------------------------------------
def test_cardenas_reference_size():
    records = (
        build_cardenas_reference()
    )

    assert len(
        records
    ) == 97


# ---------------------------------------------------------------------------
# CHEMICAL POTENTIAL TO ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def test_chemical_potential_to_electronegativity():
    record = (
        build_cardenas_element_record(
            element_symbol="Pr",
            chemical_potential_ev=-3.22,
        )
    )

    assert (
        record.chemical_potential_ev
        == pytest.approx(
            -3.22
        )
    )

    assert (
        record.absolute_electronegativity_ev
        == pytest.approx(
            3.22
        )
    )


# ---------------------------------------------------------------------------
# CARDENAS VALUES ARE TABULATED
# ---------------------------------------------------------------------------
def test_cardenas_values_are_tabulated():
    record = (
        build_cardenas_element_record(
            element_symbol="Nd",
            chemical_potential_ev=-2.85,
        )
    )

    assert (
        record.value_status
        == (
            ElectronegativityValueStatus
            .TABULATED
        )
    )

    assert (
        record.source_name
        == CARDENAS_SOURCE_NAME
    )

    assert (
        record.source_reference
        == CARDENAS_SOURCE_REFERENCE
    )


# ---------------------------------------------------------------------------
# CARDENAS RARE EARTH COVERAGE
# ---------------------------------------------------------------------------
def test_cardenas_rare_earth_coverage():
    lookup = (
        build_cardenas_lookup()
    )

    expected = {
        "La",
        "Ce",
        "Pr",
        "Nd",
        "Pm",
        "Sm",
        "Eu",
        "Gd",
        "Tb",
        "Dy",
        "Ho",
        "Er",
        "Tm",
        "Yb",
        "Lu",
    }

    assert expected.issubset(
        lookup
    )


# ---------------------------------------------------------------------------
# CARDENAS RARE EARTH VALUES
# ---------------------------------------------------------------------------
def test_cardenas_rare_earth_values():
    lookup = (
        build_cardenas_lookup()
    )

    assert (
        lookup[
            "La"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.03
        )
    )

    assert (
        lookup[
            "Pr"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.22
        )
    )

    assert (
        lookup[
            "Gd"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.15
        )
    )

    assert (
        lookup[
            "Lu"
        ].absolute_electronegativity_ev
        == pytest.approx(
            2.88
        )
    )


# ---------------------------------------------------------------------------
# COMMON PSK/TMD ELEMENT VALUES
# ---------------------------------------------------------------------------
def test_common_psk_tmd_element_values():
    lookup = (
        build_cardenas_lookup()
    )

    assert (
        lookup[
            "O"
        ].absolute_electronegativity_ev
        == pytest.approx(
            7.54
        )
    )

    assert (
        lookup[
            "Ti"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.45
        )
    )

    assert (
        lookup[
            "Mo"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.92
        )
    )

    assert (
        lookup[
            "W"
        ].absolute_electronegativity_ev
        == pytest.approx(
            4.35
        )
    )

    assert (
        lookup[
            "S"
        ].absolute_electronegativity_ev
        == pytest.approx(
            6.22
        )
    )


# ---------------------------------------------------------------------------
# EVERY VALUE SATISFIES CHI EQUALS NEGATIVE MU
# ---------------------------------------------------------------------------
def test_every_value_satisfies_chi_equals_negative_mu():
    records = (
        build_cardenas_reference()
    )

    for record in records:
        assert (
            record.absolute_electronegativity_ev
            == pytest.approx(
                -record.chemical_potential_ev
            )
        )


# ---------------------------------------------------------------------------
# NO DUPLICATE ELEMENTS
# ---------------------------------------------------------------------------
def test_no_duplicate_elements():
    records = (
        build_cardenas_reference()
    )

    symbols = [
        record.element_symbol
        for record in records
    ]

    assert len(
        symbols
    ) == len(
        set(
            symbols
        )
    )


# ---------------------------------------------------------------------------
# POSITIVE CHEMICAL POTENTIAL FAILS
# ---------------------------------------------------------------------------
def test_positive_chemical_potential_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be negative"
        ),
    ):
        build_cardenas_element_record(
            element_symbol="X",
            chemical_potential_ev=1.0,
        )


# ---------------------------------------------------------------------------
# SOURCE TABLE HAS EXPECTED SIZE
# ---------------------------------------------------------------------------
def test_source_table_has_expected_size():
    assert len(
        CARDENAS_NEUTRAL_CHEMICAL_POTENTIAL_EV
    ) == 97


