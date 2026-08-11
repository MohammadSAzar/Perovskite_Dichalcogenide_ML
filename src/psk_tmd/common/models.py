from datetime import date

from pydantic import BaseModel, Field

from psk_tmd.common.constants import (
    AccessType,
    ChargeTransferClass,
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    ExtractorType,
    FractionBasis,
    LabelStatus,
    ManualReviewStatus,
    MechanismLabel,
    PhotocatalyticApplication,
    SynthesisStepRole,
    SynthesisTopology,
)


# ---------------------------------------------------------------------------
# PAPER AND SOURCE METADATA
# ---------------------------------------------------------------------------
class PaperRecord(BaseModel):
    paper_id: str
    doi: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int = Field(ge=1900)
    journal: str | None = None
    publisher: str | None = None
    document_type: str | None = None
    access_type: AccessType = AccessType.UNKNOWN
    full_text_available: bool = False
    source_url: str | None = None
    retrieval_date: date | None = None


# ---------------------------------------------------------------------------
# MATERIAL DESCRIPTIONS
# ---------------------------------------------------------------------------
class PSKDescription(BaseModel):
    formula_reported: str
    formula_normalized: str | None = None
    parent_formula: str | None = None

    a_site_elements: list[str] = Field(default_factory=list)
    b_site_elements: list[str] = Field(default_factory=list)
    anion_site_elements: list[str] = Field(default_factory=list)

    a_site_dopants: list[str] = Field(default_factory=list)
    b_site_dopants: list[str] = Field(default_factory=list)
    anion_site_dopants: list[str] = Field(default_factory=list)

    phase_reported: str | None = None
    space_group_reported: str | None = None
    morphology: str | None = None
    particle_size_nm: float | None = Field(default=None, ge=0)
    defects_reported: str | None = None
    doping_description: str | None = None
    commercial: bool | None = None


class TMDDescription(BaseModel):
    formula_reported: str
    formula_normalized: str | None = None
    parent_formula: str | None = None

    m_site_elements: list[str] = Field(default_factory=list)
    x_site_elements: list[str] = Field(default_factory=list)

    m_site_dopants: list[str] = Field(default_factory=list)
    x_site_dopants: list[str] = Field(default_factory=list)

    phase_reported: str | None = None
    layer_description: str | None = None
    morphology: str | None = None
    particle_size_nm: float | None = Field(default=None, ge=0)
    defects_reported: str | None = None
    doping_description: str | None = None
    commercial: bool | None = None


class HeterostructureDescription(BaseModel):
    heterostructure_type_reported: str | None = None
    component_ratio_reported: str | None = None
    interface_description: str | None = None
    contact_type: str | None = None
    preferred_facet_reported: str | None = None

    cocatalyst_present: bool | None = None
    cocatalyst: str | None = None

    mediator_present: bool | None = None
    mediator: str | None = None

    morphology: str | None = None
    interface_notes: str | None = None


# ---------------------------------------------------------------------------
# EXPERIMENTAL SAMPLES
# ---------------------------------------------------------------------------
class ExperimentalSample(BaseModel):
    sample_id: str
    paper_id: str
    sample_name_reported: str | None = None

    psk: PSKDescription
    tmd: TMDDescription
    heterostructure: HeterostructureDescription | None = None

    pair_id: str | None = None

    psk_fraction: float | None = Field(default=None, ge=0)
    tmd_fraction: float | None = Field(default=None, ge=0)
    fraction_basis: FractionBasis | None = None

    is_reference_sample: bool = False
    notes: str | None = None


# ---------------------------------------------------------------------------
# SYNTHESIS
# ---------------------------------------------------------------------------
class SynthesisStep(BaseModel):
    synthesis_step_id: str
    sample_id: str
    step_order: int = Field(ge=1)

    step_role: SynthesisStepRole = SynthesisStepRole.UNKNOWN
    topology: SynthesisTopology | None = None

    method: str | None = None
    precursors: list[str] = Field(default_factory=list)

    temperature_c: float | None = None
    time_h: float | None = Field(default=None, ge=0)
    pressure: str | None = None
    atmosphere: str | None = None
    solvent: str | None = None
    ph: float | None = None

    calcination_temperature_c: float | None = None
    calcination_time_h: float | None = Field(default=None, ge=0)

    raw_description: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER MECHANISM
# ---------------------------------------------------------------------------
class MechanismAssessment(BaseModel):
    mechanism_assessment_id: str
    sample_id: str

    mechanism_reported: str | None = None
    mechanism_normalized: MechanismLabel = MechanismLabel.UNKNOWN
    charge_transfer_class: ChargeTransferClass | None = None

    claim_explicit: bool | None = None
    assessment_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    manual_review_status: ManualReviewStatus = ManualReviewStatus.PENDING
    label_status: LabelStatus = LabelStatus.PENDING_REVIEW
    reviewer_notes: str | None = None


class MechanismEvidence(BaseModel):
    evidence_id: str
    mechanism_assessment_id: str

    evidence_type: EvidenceType = EvidenceType.UNKNOWN
    evidence_subtype: str | None = None

    support: EvidenceSupport = EvidenceSupport.UNKNOWN
    evidence_strength: EvidenceStrength = EvidenceStrength.UNKNOWN

    reported_result: str | None = None
    source_location: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# PHOTOCATALYTIC TESTS
# ---------------------------------------------------------------------------
class PhotocatalyticTest(BaseModel):
    test_id: str
    sample_id: str

    application_type: PhotocatalyticApplication = (
        PhotocatalyticApplication.UNKNOWN
    )
    reaction_type: str | None = None
    target_species: str | None = None

    light_source: str | None = None
    wavelength_nm: float | None = Field(default=None, ge=0)
    light_intensity: str | None = None
    visible_light_only: bool | None = None

    catalyst_mass_mg: float | None = Field(default=None, ge=0)
    solution_volume_ml: float | None = Field(default=None, ge=0)
    ph: float | None = None
    sacrificial_agent: str | None = None
    cocatalyst: str | None = None
    test_duration_h: float | None = Field(default=None, ge=0)

    performance_metric_name: str | None = None
    performance_metric_value: float | None = None
    performance_metric_unit: str | None = None

    hydrogen_amount_umol: float | None = Field(default=None, ge=0)
    hydrogen_rate_reported_value: float | None = Field(default=None, ge=0)
    hydrogen_rate_reported_unit: str | None = None
    hydrogen_rate_standardized_umol_g_h: float | None = Field(
        default=None,
        ge=0,
    )

    sth_percent: float | None = Field(default=None, ge=0)
    apparent_quantum_yield_percent: float | None = Field(
        default=None,
        ge=0,
    )

    cycles: int | None = Field(default=None, ge=0)
    performance_notes: str | None = None


# ---------------------------------------------------------------------------
# EXTRACTION AND PROVENANCE
# ---------------------------------------------------------------------------
class ExtractionRecord(BaseModel):
    extraction_id: str
    paper_id: str

    target_table: str | None = None
    target_record_id: str | None = None
    target_field: str | None = None

    extractor_type: ExtractorType = ExtractorType.UNKNOWN
    extractor_name: str | None = None
    extractor_version: str | None = None
    extraction_date: date | None = None

    source_location: str | None = None
    raw_value: str | None = None
    normalized_value: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    manual_verified: bool = False
    reviewer: str | None = None
    notes: str | None = None

