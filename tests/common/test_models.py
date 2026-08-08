import pytest

from pydantic import ValidationError

from psk_tmd.common.constants import (
    DataSource,
    MappingStatus,
    MaterialType,
    MechanismLabel,
)
from psk_tmd.common.models import (
    ExperimentalSample,
    MappingRecord,
    MaterialRecord,
    PaperRecord,
)


def test_paper_record():
    paper = PaperRecord(
        paper_id="PPR-000001",
        doi="10.1234/example",
        title="Example paper",
    )

    assert paper.paper_id == "PPR-000001"


def test_experimental_sample():
    sample = ExperimentalSample(
        sample_id="SMP-000001",
        paper_id="PPR-000001",
        psk_formula="CaTiO3",
        tmd_formula="MoS2",
        mechanism=MechanismLabel.Z_SCHEME,
    )

    assert sample.psk_formula == "CaTiO3"
    assert sample.mechanism == MechanismLabel.Z_SCHEME


def test_material_record():
    material = MaterialRecord(
        source=DataSource.MP,
        source_record_id="mp-example",
        material_type=MaterialType.PSK,
        formula="CaTiO3",
        band_gap_ev=3.2,
    )

    assert material.source == DataSource.MP
    assert material.band_gap_ev == 3.2


def test_negative_band_gap_is_rejected():
    with pytest.raises(ValidationError):
        MaterialRecord(
            source=DataSource.MP,
            source_record_id="mp-example",
            material_type=MaterialType.PSK,
            formula="CaTiO3",
            band_gap_ev=-1.0,
        )


def test_mapping_confidence_must_be_between_zero_and_one():
    with pytest.raises(ValidationError):
        MappingRecord(
            mapping_id="MAP-000001",
            sample_id="SMP-000001",
            source=DataSource.MP,
            source_record_id="mp-example",
            status=MappingStatus.PROBABLE,
            confidence=1.2,
        )

