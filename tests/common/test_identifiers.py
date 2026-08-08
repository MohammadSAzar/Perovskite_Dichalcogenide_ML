import pytest

from psk_tmd.common.identifiers import (
    EntityPrefix,
    make_sequential_id,
)


def test_make_sample_id():
    result = make_sequential_id(
        EntityPrefix.SAMPLE,
        1,
    )

    assert result == "SMP-000001"


def test_make_mapping_id():
    result = make_sequential_id(
        EntityPrefix.MAPPING,
        42,
    )

    assert result == "MAP-000042"


def test_custom_width():
    result = make_sequential_id(
        EntityPrefix.COMPOSITION,
        7,
        width=4,
    )

    assert result == "CMP-0007"


def test_invalid_number_raises_error():
    with pytest.raises(ValueError):
        make_sequential_id(
            EntityPrefix.SAMPLE,
            0,
        )


def test_invalid_width_raises_error():
    with pytest.raises(ValueError):
        make_sequential_id(
            EntityPrefix.SAMPLE,
            1,
            width=0,
        )

