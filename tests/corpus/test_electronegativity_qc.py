import json
import pytest

from pathlib import Path

from psk_tmd.common.constants import (
    ElectronegativityValueStatus,
)
from psk_tmd.common.models import (
    ElementElectronegativityRecord,
)
from psk_tmd.corpus.electronegativity_qc import (
    compare_electronegativity_references,
    get_flagged_comparisons,
    load_electronegativity_reference,
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
# COMPARE COMMON AVAILABLE VALUES
# ---------------------------------------------------------------------------
def test_compare_common_available_values():
    canonical = [
        make_record(
            "La",
            3.03,
        ),
        make_record(
            "O",
            7.54,
        ),
    ]

    validation = [
        make_record(
            "La",
            3.0385,
        ),
        make_record(
            "O",
            7.5395,
        ),
    ]

    comparisons = (
        compare_electronegativity_references(
            canonical_records=canonical,
            validation_records=validation,
            discrepancy_threshold_ev=0.10,
        )
    )

    lookup = {
        comparison.element_symbol:
        comparison
        for comparison in comparisons
    }

    assert (
        lookup[
            "La"
        ].delta_ev
        == pytest.approx(
            -0.0085
        )
    )

    assert (
        lookup[
            "La"
        ].absolute_delta_ev
        == pytest.approx(
            0.0085
        )
    )

    assert not (
        lookup[
            "La"
        ].exceeds_threshold
    )


# ---------------------------------------------------------------------------
# UNAVAILABLE VALIDATION VALUE IS SKIPPED
# ---------------------------------------------------------------------------
def test_unavailable_validation_value_is_skipped():
    canonical = [
        make_record(
            "Pr",
            3.22,
        ),
    ]

    validation = [
        make_record(
            "Pr",
            None,
        ),
    ]

    comparisons = (
        compare_electronegativity_references(
            canonical_records=canonical,
            validation_records=validation,
            discrepancy_threshold_ev=0.10,
        )
    )

    assert comparisons == []


# ---------------------------------------------------------------------------
# LARGE DISCREPANCY IS FLAGGED
# ---------------------------------------------------------------------------
def test_large_discrepancy_is_flagged():
    canonical = [
        make_record(
            "X",
            4.00,
        ),
    ]

    validation = [
        make_record(
            "X",
            3.50,
        ),
    ]

    comparisons = (
        compare_electronegativity_references(
            canonical_records=canonical,
            validation_records=validation,
            discrepancy_threshold_ev=0.25,
        )
    )

    assert len(
        comparisons
    ) == 1

    assert (
        comparisons[
            0
        ].exceeds_threshold
    )


# ---------------------------------------------------------------------------
# GET FLAGGED COMPARISONS
# ---------------------------------------------------------------------------
def test_get_flagged_comparisons():
    canonical = [
        make_record(
            "A",
            3.00,
        ),
        make_record(
            "B",
            4.00,
        ),
    ]

    validation = [
        make_record(
            "A",
            3.05,
        ),
        make_record(
            "B",
            3.50,
        ),
    ]

    comparisons = (
        compare_electronegativity_references(
            canonical_records=canonical,
            validation_records=validation,
            discrepancy_threshold_ev=0.25,
        )
    )

    flagged = (
        get_flagged_comparisons(
            comparisons
        )
    )

    assert len(
        flagged
    ) == 1

    assert (
        flagged[
            0
        ].element_symbol
        == "B"
    )


# ---------------------------------------------------------------------------
# NEGATIVE THRESHOLD FAILS
# ---------------------------------------------------------------------------
def test_negative_threshold_fails():
    with pytest.raises(
        ValueError,
        match=(
            "must be non-negative"
        ),
    ):
        compare_electronegativity_references(
            canonical_records=[],
            validation_records=[],
            discrepancy_threshold_ev=-0.1,
        )


# ---------------------------------------------------------------------------
# LOAD REFERENCE
# ---------------------------------------------------------------------------
def test_load_reference(
    tmp_path: Path,
):
    path = (
        tmp_path
        / "reference.json"
    )

    payload = {
        "records": [
            make_record(
                "O",
                7.54,
            ).model_dump(
                mode="json"
            )
        ]
    }

    path.write_text(
        json.dumps(
            payload
        ),
        encoding="utf-8",
    )

    records = (
        load_electronegativity_reference(
            path
        )
    )

    assert len(
        records
    ) == 1

    assert (
        records[
            0
        ].element_symbol
        == "O"
    )

