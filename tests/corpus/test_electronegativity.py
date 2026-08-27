import pytest

from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)
from psk_tmd.corpus.electronegativity import (
    build_element_electronegativity_lookup,
    calculate_atomic_absolute_electronegativity,
    parse_optional_float,
    parse_pubchem_periodic_table,
    merge_electronegativity_references,
    resolve_element_electronegativity,
)


# ---------------------------------------------------------------------------
# MAKE PUBCHEM PAYLOAD
# ---------------------------------------------------------------------------
def make_pubchem_payload():
    return {
        "Table": {
            "Columns": {
                "Column": [
                    "AtomicNumber",
                    "Symbol",
                    "Name",
                    "IonizationEnergy",
                    "ElectronAffinity",
                ]
            },
            "Row": [
                {
                    "Cell": [
                        "8",
                        "O",
                        "Oxygen",
                        "13.618",
                        "1.461",
                    ]
                },
                {
                    "Cell": [
                        "57",
                        "La",
                        "Lanthanum",
                        "5.577",
                        "0.5",
                    ]
                },
                {
                    "Cell": [
                        "59",
                        "Pr",
                        "Praseodymium",
                        "5.464",
                        "",
                    ]
                },
            ],
        }
    }


# ---------------------------------------------------------------------------
# PARSE OPTIONAL FLOAT
# ---------------------------------------------------------------------------
def test_parse_optional_float():
    assert (
        parse_optional_float(
            "1.25"
        )
        == pytest.approx(
            1.25
        )
    )

    assert (
        parse_optional_float(
            ""
        )
        is None
    )

    assert (
        parse_optional_float(
            None
        )
        is None
    )


# ---------------------------------------------------------------------------
# INVALID OPTIONAL FLOAT FAILS
# ---------------------------------------------------------------------------
def test_invalid_optional_float_fails():
    with pytest.raises(
        ValueError,
        match=(
            "Could not parse numeric value"
        ),
    ):
        parse_optional_float(
            "not-a-number"
        )


# ---------------------------------------------------------------------------
# CALCULATE ATOMIC ABSOLUTE ELECTRONEGATIVITY
# ---------------------------------------------------------------------------
def test_calculate_atomic_absolute_electronegativity():
    result = (
        calculate_atomic_absolute_electronegativity(
            ionization_energy_ev=(
                13.618
            ),
            electron_affinity_ev=(
                1.461
            ),
        )
    )

    assert result == pytest.approx(
        7.5395
    )


# ---------------------------------------------------------------------------
# NEGATIVE IONIZATION ENERGY FAILS
# ---------------------------------------------------------------------------
def test_negative_ionization_energy_fails():
    with pytest.raises(
        ValueError,
        match=(
            "Ionization energy must be "
            "non-negative"
        ),
    ):
        calculate_atomic_absolute_electronegativity(
            ionization_energy_ev=-1.0,
            electron_affinity_ev=1.0,
        )


# ---------------------------------------------------------------------------
# PARSE COMPLETE PUBCHEM ELEMENT
# ---------------------------------------------------------------------------
def test_parse_complete_pubchem_element():
    records = (
        parse_pubchem_periodic_table(
            make_pubchem_payload(),
            source_reference=(
                "test_reference"
            ),
        )
    )

    oxygen = records[
        0
    ]

    assert (
        oxygen.element_symbol
        == "O"
    )

    assert (
        oxygen.value_status
        == (
            ElectronegativityValueStatus
            .DERIVED_IE_EA
        )
    )

    assert (
        oxygen.absolute_electronegativity_ev
        == pytest.approx(
            7.5395
        )
    )

    assert (
        oxygen.source_reference
        == "test_reference"
    )


# ---------------------------------------------------------------------------
# PARSE RARE EARTH WITH DATA
# ---------------------------------------------------------------------------
def test_parse_rare_earth_with_data():
    records = (
        parse_pubchem_periodic_table(
            make_pubchem_payload()
        )
    )

    lanthanum = records[
        1
    ]

    assert (
        lanthanum.element_symbol
        == "La"
    )

    assert (
        lanthanum.absolute_electronegativity_ev
        == pytest.approx(
            3.0385
        )
    )

    assert (
        lanthanum.value_status
        == (
            ElectronegativityValueStatus
            .DERIVED_IE_EA
        )
    )


# ---------------------------------------------------------------------------
# MISSING ELECTRON AFFINITY IS UNAVAILABLE
# ---------------------------------------------------------------------------
def test_missing_electron_affinity_is_unavailable():
    records = (
        parse_pubchem_periodic_table(
            make_pubchem_payload()
        )
    )

    praseodymium = records[
        2
    ]

    assert (
        praseodymium.element_symbol
        == "Pr"
    )

    assert (
        praseodymium.ionization_energy_ev
        == pytest.approx(
            5.464
        )
    )

    assert (
        praseodymium.electron_affinity_ev
        is None
    )

    assert (
        praseodymium.absolute_electronegativity_ev
        is None
    )

    assert (
        praseodymium.value_status
        == (
            ElectronegativityValueStatus
            .UNAVAILABLE
        )
    )


# ---------------------------------------------------------------------------
# BUILD ELEMENT LOOKUP
# ---------------------------------------------------------------------------
def test_build_element_lookup():
    records = (
        parse_pubchem_periodic_table(
            make_pubchem_payload()
        )
    )

    lookup = (
        build_element_electronegativity_lookup(
            records
        )
    )

    assert (
        set(
            lookup
        )
        == {
            "O",
            "La",
            "Pr",
        }
    )


# ---------------------------------------------------------------------------
# DUPLICATE ELEMENT FAILS
# ---------------------------------------------------------------------------
def test_duplicate_element_fails():
    records = [
        ElementElectronegativityRecord(
            element_symbol="O",
        ),
        ElementElectronegativityRecord(
            element_symbol="O",
        ),
    ]

    with pytest.raises(
        ValueError,
        match=(
            "Duplicate elemental "
            "electronegativity record"
        ),
    ):
        build_element_electronegativity_lookup(
            records
        )


# ---------------------------------------------------------------------------
# PRIMARY ELECTRONEGATIVITY WINS
# ---------------------------------------------------------------------------
def test_primary_electronegativity_wins():
    primary = (
        ElementElectronegativityRecord(
            element_symbol="La",
            absolute_electronegativity_ev=(
                3.0385
            ),
            value_status=(
                ElectronegativityValueStatus
                .DERIVED_IE_EA
            ),
        )
    )

    fallback = (
        ElementElectronegativityRecord(
            element_symbol="La",
            absolute_electronegativity_ev=(
                3.20
            ),
            value_status=(
                ElectronegativityValueStatus
                .ESTIMATED
            ),
        )
    )

    resolved = (
        resolve_element_electronegativity(
            primary=primary,
            fallback=fallback,
        )
    )

    assert (
        resolved.absolute_electronegativity_ev
        == pytest.approx(
            3.0385
        )
    )

    assert (
        resolved.value_status
        == (
            ElectronegativityValueStatus
            .DERIVED_IE_EA
        )
    )


# ---------------------------------------------------------------------------
# FALLBACK FILLS MISSING VALUE
# ---------------------------------------------------------------------------
def test_fallback_fills_missing_value():
    primary = (
        ElementElectronegativityRecord(
            element_symbol="Pr",
        )
    )

    fallback = (
        ElementElectronegativityRecord(
            element_symbol="Pr",
            absolute_electronegativity_ev=(
                3.10
            ),
            value_status=(
                ElectronegativityValueStatus
                .ESTIMATED
            ),
            source_name="test_fallback",
            estimation_method=(
                "test estimate"
            ),
        )
    )

    resolved = (
        resolve_element_electronegativity(
            primary=primary,
            fallback=fallback,
        )
    )

    assert (
        resolved.absolute_electronegativity_ev
        == pytest.approx(
            3.10
        )
    )

    assert (
        resolved.value_status
        == (
            ElectronegativityValueStatus
            .ESTIMATED
        )
    )


# ---------------------------------------------------------------------------
# MISSING FALLBACK PRESERVES UNAVAILABLE
# ---------------------------------------------------------------------------
def test_missing_fallback_preserves_unavailable():
    primary = (
        ElementElectronegativityRecord(
            element_symbol="Nd",
        )
    )

    resolved = (
        resolve_element_electronegativity(
            primary=primary,
            fallback=None,
        )
    )

    assert (
        resolved.absolute_electronegativity_ev
        is None
    )

    assert (
        resolved.value_status
        == (
            ElectronegativityValueStatus
            .UNAVAILABLE
        )
    )


# ---------------------------------------------------------------------------
# FALLBACK SYMBOL MUST MATCH
# ---------------------------------------------------------------------------
def test_fallback_symbol_must_match():
    primary = (
        ElementElectronegativityRecord(
            element_symbol="Pr",
        )
    )

    fallback = (
        ElementElectronegativityRecord(
            element_symbol="Nd",
            absolute_electronegativity_ev=(
                3.0
            ),
            value_status=(
                ElectronegativityValueStatus
                .ESTIMATED
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "symbols do not match"
        ),
    ):
        resolve_element_electronegativity(
            primary=primary,
            fallback=fallback,
        )


# ---------------------------------------------------------------------------
# MERGE REFERENCES
# ---------------------------------------------------------------------------
def test_merge_electronegativity_references():
    primary_records = [
        ElementElectronegativityRecord(
            element_symbol="La",
            absolute_electronegativity_ev=(
                3.0385
            ),
            value_status=(
                ElectronegativityValueStatus
                .DERIVED_IE_EA
            ),
        ),
        ElementElectronegativityRecord(
            element_symbol="Pr",
        ),
    ]

    fallback_records = [
        ElementElectronegativityRecord(
            element_symbol="Pr",
            absolute_electronegativity_ev=(
                3.10
            ),
            value_status=(
                ElectronegativityValueStatus
                .ESTIMATED
            ),
        ),
    ]

    resolved = (
        merge_electronegativity_references(
            primary_records=(
                primary_records
            ),
            fallback_records=(
                fallback_records
            ),
        )
    )

    lookup = {
        record.element_symbol: record
        for record in resolved
    }

    assert (
        lookup[
            "La"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.0385
        )
    )

    assert (
        lookup[
            "Pr"
        ].absolute_electronegativity_ev
        == pytest.approx(
            3.10
        )
    )

