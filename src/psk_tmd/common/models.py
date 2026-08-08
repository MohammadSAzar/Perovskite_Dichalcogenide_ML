from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    DataSource,
    MappingStatus,
    MaterialType,
    MechanismLabel,
)


class PaperRecord(BaseModel):
    """
    Minimal bibliographic record for a scientific publication.
    """

    paper_id: str
    doi: str | None = None
    title: str | None = None


class ExperimentalSample(BaseModel):
    """
    Minimal record for one experimentally reported PSK-TMD sample
    or sample condition.
    """

    sample_id: str
    paper_id: str

    psk_formula: str
    tmd_formula: str

    mechanism: MechanismLabel = MechanismLabel.UNKNOWN


class MaterialRecord(BaseModel):
    """
    Minimal source-native computational material record.
    """

    source: DataSource
    source_record_id: str

    material_type: MaterialType
    formula: str

    band_gap_ev: float | None = Field(
        default=None,
        ge=0,
    )


class MappingRecord(BaseModel):
    """
    Relationship between one experimental sample and one
    computational material record.
    """

    mapping_id: str
    sample_id: str

    source: DataSource
    source_record_id: str

    status: MappingStatus

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    notes: str | None = None

