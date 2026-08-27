from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.corpus.electronegativity import (
    build_electronegativity_reference_payload,
)


# ----------------------------------------------------------------------------
# MAKE TEST PAYLOAD
# ----------------------------------------------------------------------------
def make_test_payload():
    return {
        "Table": {
            "Columns": {
                "Column": [
                    "AtomicNumber",
                    "Symbol",
                    "IonizationEnergy",
                    "ElectronAffinity",
                ]
            },
            "Row": [
                {
                    "Cell": [
                        "8",
                        "O",
                        "13.618",
                        "1.461",
                    ]
                },
                {
                    "Cell": [
                        "59",
                        "Pr",
                        "5.464",
                        "",
                    ]
                },
            ],
        }
    }


# ----------------------------------------------------------------------------
# BUILD OUTPUT PAYLOAD
# ----------------------------------------------------------------------------
def test_build_output_payload():
    result = (
        build_electronegativity_reference_payload(
            make_test_payload(),
            source_url="test_url",
            retrieval_date="2026-08-21",
        )
    )

    assert (
        result[
            "source_name"
        ]
        == "PubChem Periodic Table"
    )

    assert (
            result[
                "method"
            ]
            == (
                "absolute electronegativity "
                "derived as (IE + EA) / 2; "
                "chemical potential derived "
                "as -(IE + EA) / 2"
            )
    )

    assert len(
        result[
            "records"
        ]
    ) == 2


# ----------------------------------------------------------------------------
# OUTPUT PRESERVES UNAVAILABLE ELEMENT
# ----------------------------------------------------------------------------
def test_output_preserves_unavailable_element():
    result = (
        build_electronegativity_reference_payload(
            make_test_payload(),
            source_url="test_url",
            retrieval_date="2026-08-21",
        )
    )

    records = {
        record[
            "element_symbol"
        ]: record
        for record
        in result[
            "records"
        ]
    }

    assert (
        records[
            "O"
        ][
            "value_status"
        ]
        == (
            ElectronegativityValueStatus
            .DERIVED_IE_EA
            .value
        )
    )

    assert (
        records[
            "Pr"
        ][
            "value_status"
        ]
        == (
            ElectronegativityValueStatus
            .UNAVAILABLE
            .value
        )
    )

    assert (
        records[
            "Pr"
        ][
            "absolute_electronegativity_ev"
        ]
        is None
    )


