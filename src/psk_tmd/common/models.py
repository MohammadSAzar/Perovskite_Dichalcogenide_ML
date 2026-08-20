from datetime import date

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

from psk_tmd.common.constants import (
    AccessType,
    CharacterizationRole,
    ChargeTransferClass,
    DisagreementStatus,
    DisagreementType,
    EvidenceContextType,
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    ExtractorType,
    FractionBasis,
    LabelStatus,
    ManualReviewStatus,
    MechanismLabel,
    PaperSectionRole,
    PhotocatalyticApplication,
    ProvenanceOperation,
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
class SampleSeries(BaseModel):
    sample_series_id: str
    paper_id: str

    pair_id: str | None = None
    series_name_reported: str | None = None
    notes: str | None = None


class ExperimentalSample(BaseModel):
    sample_id: str
    paper_id: str
    sample_series_id: str | None = None
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
class SynthesisRecord(BaseModel):
    synthesis_id: str
    sample_id: str

    topology: SynthesisTopology = SynthesisTopology.UNKNOWN
    method_reported: str | None = None
    notes: str | None = None


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER MECHANISM
# ---------------------------------------------------------------------------
class MechanismAssessment(BaseModel):
    mechanism_assessment_id: str
    sample_id: str
    applies_to_series_id: str | None = None

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

    characterization_role: CharacterizationRole = (
        CharacterizationRole.OTHER
    )

    mechanism_discriminating: bool = False

    requires_context: bool = False

    required_context: list[
        EvidenceContextType
    ] = Field(
        default_factory=list,
    )

    section_role: PaperSectionRole = (
        PaperSectionRole.OTHER
    )

    section_title: str | None = None

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    @model_validator(
        mode="after"
    )
    def validate_evidence_context(
            self,
    ) -> "MechanismEvidence":
        if (
                self.requires_context
                and not self.required_context
        ):
            raise ValueError(
                "Evidence requiring context "
                "must specify required_context."
            )

        if (
                not self.requires_context
                and self.required_context
        ):
            raise ValueError(
                "required_context must be empty "
                "when requires_context is False."
            )

        return self


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

    initial_target_concentration_value: float | None = Field(
        default=None,
        ge=0,
    )
    initial_target_concentration_unit: str | None = None

    light_source: str | None = None
    wavelength_nm: float | None = Field(default=None, ge=0)
    wavelength_min_nm: float | None = Field(default=None, ge=0)
    wavelength_max_nm: float | None = Field(default=None, ge=0)

    light_intensity_value: float | None = Field(default=None, ge=0)
    light_intensity_unit: str | None = None
    visible_light_only: bool | None = None

    catalyst_mass_mg: float | None = Field(default=None, ge=0)
    solution_volume_ml: float | None = Field(default=None, ge=0)
    ph: float | None = None
    sacrificial_agent: str | None = None
    cocatalyst: str | None = None

    dark_equilibration_time_min: float | None = Field(
        default=None,
        ge=0,
    )
    test_duration_h: float | None = Field(default=None, ge=0)

    performance_metric_name: str | None = None
    performance_metric_value: float | None = None
    performance_metric_unit: str | None = None

    cycles: int | None = Field(default=None, ge=1)
    first_cycle_performance: float | None = None
    last_cycle_performance: float | None = None

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

    provenance_operation: ProvenanceOperation = ProvenanceOperation.UNKNOWN

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


# ---------------------------------------------------------------------------
# DISAGREEMENTS AND SOURCE CONFLICTS
# ---------------------------------------------------------------------------
class DisagreementRecord(BaseModel):
    disagreement_id: str
    disagreement_type: DisagreementType
    status: DisagreementStatus = DisagreementStatus.UNRESOLVED

    paper_ids: list[str] = Field(default_factory=list)
    target_table: str | None = None
    target_record_ids: list[str] = Field(default_factory=list)
    target_field: str | None = None

    reported_values: list[str] = Field(min_length=1)
    selected_value: str | None = None

    description: str | None = None
    resolution_notes: str | None = None


