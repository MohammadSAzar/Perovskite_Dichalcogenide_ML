import pytest

from pydantic import ValidationError

from psk_tmd.common.constants import (
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
    MechanismLabel,
    PaperSectionRole,
    PhotocatalyticApplication,
    ProvenanceOperation,
    SynthesisTopology,
    ManualReviewStatus,
)

from psk_tmd.common.models import (
    ExperimentalSample,
    ExtractionRecord,
    HeterostructureDescription,
    MechanismAssessment,
    MechanismEvidence,
    PairRecord,
    PaperRecord,
    PhotocatalyticTest,
    PSKDescription,
    SynthesisRecord,
    TMDDescription,
    DisagreementRecord,
    SampleSeries,
    PairMechanismLabel,
)


# ---------------------------------------------------------------------------
# PAPER RECORDS
# ---------------------------------------------------------------------------
def test_paper_record_valid():
    paper = PaperRecord(
        paper_id="PPR-000001",
        title="Example PSK-TMD photocatalysis paper",
        year=2024,
    )

    assert paper.paper_id == "PPR-000001"
    assert paper.year == 2024
    assert paper.authors == []


def test_paper_record_rejects_invalid_year():
    with pytest.raises(ValidationError):
        PaperRecord(
            paper_id="PPR-000001",
            title="Invalid paper",
            year=1800,
        )


# ---------------------------------------------------------------------------
# PSK DESCRIPTIONS
# ---------------------------------------------------------------------------
def test_psk_description_with_doping():
    psk = PSKDescription(
        formula_reported="La0.8Sr0.2FeO3",
        parent_formula="LaFeO3",
        a_site_elements=["La", "Sr"],
        b_site_elements=["Fe"],
        anion_site_elements=["O"],
        a_site_dopants=["Sr"],
    )

    assert psk.parent_formula == "LaFeO3"
    assert psk.a_site_dopants == ["Sr"]
    assert psk.b_site_dopants == []


def test_psk_description_allows_multiple_site_dopants():
    psk = PSKDescription(
        formula_reported="Example-doped-PSK",
        a_site_elements=["A1", "A2", "A3"],
        b_site_elements=["B1", "B2"],
        anion_site_elements=["O", "X1"],
        a_site_dopants=["A2", "A3"],
        b_site_dopants=["B2"],
        anion_site_dopants=["X1"],
    )

    assert len(psk.a_site_dopants) == 2
    assert len(psk.b_site_dopants) == 1
    assert len(psk.anion_site_dopants) == 1


# ---------------------------------------------------------------------------
# TMD DESCRIPTIONS
# ---------------------------------------------------------------------------
def test_tmd_description_with_m_site_doping():
    tmd = TMDDescription(
        formula_reported="Mo0.9W0.1S2",
        parent_formula="MoS2",
        m_site_elements=["Mo", "W"],
        x_site_elements=["S"],
        m_site_dopants=["W"],
    )

    assert tmd.m_site_dopants == ["W"]
    assert tmd.x_site_dopants == []


def test_tmd_description_with_x_site_doping():
    tmd = TMDDescription(
        formula_reported="MoS1.8Se0.2",
        parent_formula="MoS2",
        m_site_elements=["Mo"],
        x_site_elements=["S", "Se"],
        x_site_dopants=["Se"],
    )

    assert tmd.x_site_dopants == ["Se"]
    assert tmd.m_site_dopants == []


def test_tmd_description_allows_multiple_m_and_x_site_dopants():
    tmd = TMDDescription(
        formula_reported="Example-multidoped-TMD",
        m_site_elements=["Mo", "W", "Co"],
        x_site_elements=["S", "Se", "Te"],
        m_site_dopants=["W", "Co"],
        x_site_dopants=["Se", "Te"],
    )

    assert tmd.m_site_dopants == ["W", "Co"]
    assert tmd.x_site_dopants == ["Se", "Te"]


def test_tmd_description_rejects_negative_particle_size():
    with pytest.raises(ValidationError):
        TMDDescription(
            formula_reported="MoS2",
            particle_size_nm=-5,
        )


# ---------------------------------------------------------------------------
# HETEROSTRUCTURE DESCRIPTIONS
# ---------------------------------------------------------------------------
def test_heterostructure_description_valid():
    heterostructure = HeterostructureDescription(
        component_ratio_reported="1:2",
        interface_description="Direct interfacial contact",
        morphology="2D/2D",
    )

    assert heterostructure.component_ratio_reported == "1:2"
    assert heterostructure.morphology == "2D/2D"


# ---------------------------------------------------------------------------
# PSK-TMD PAIRS
# ---------------------------------------------------------------------------
def test_pair_record_valid():
    pair = PairRecord(
        pair_id="PAIR-000001",
        psk_formula_reported="LaNiO3",
        psk_formula_normalized="LaNiO3",
        tmd_formula_reported="WS2",
        tmd_formula_normalized="WS2",
    )

    assert pair.pair_id == "PAIR-000001"

    assert (
        pair.psk_formula_normalized
        == "LaNiO3"
    )

    assert (
        pair.tmd_formula_normalized
        == "WS2"
    )


def test_pair_record_preserves_doped_compositions():
    pair = PairRecord(
        pair_id="PAIR-000002",
        psk_formula_reported=(
            "La0.8Sr0.2FeO3"
        ),
        psk_formula_normalized=(
            "La0.8Sr0.2FeO3"
        ),
        tmd_formula_reported=(
            "MoS1.8Se0.2"
        ),
        tmd_formula_normalized=(
            "MoS1.8Se0.2"
        ),
    )

    assert (
        pair.psk_formula_normalized
        == "La0.8Sr0.2FeO3"
    )

    assert (
        pair.tmd_formula_normalized
        == "MoS1.8Se0.2"
    )


def test_pair_record_does_not_require_normalized_formulas():
    pair = PairRecord(
        pair_id="PAIR-000003",
        psk_formula_reported="CaTiO3",
        tmd_formula_reported="MoS2",
    )

    assert (
        pair.psk_formula_normalized
        is None
    )

    assert (
        pair.tmd_formula_normalized
        is None
    )


# ---------------------------------------------------------------------------
# EXPERIMENTAL SAMPLES
# ---------------------------------------------------------------------------
def test_experimental_sample_with_nested_materials():
    sample = ExperimentalSample(
        sample_id="SMP-000001",
        paper_id="PPR-000001",
        sample_name_reported="20 wt% MoS2/CaTiO3",
        psk=PSKDescription(
            formula_reported="CaTiO3",
        ),
        tmd=TMDDescription(
            formula_reported="MoS2",
        ),
        heterostructure=HeterostructureDescription(
            component_ratio_reported="20 wt% MoS2",
        ),
        tmd_fraction=20,
        fraction_basis=FractionBasis.WEIGHT_PERCENT,
    )

    assert sample.psk.formula_reported == "CaTiO3"
    assert sample.tmd.formula_reported == "MoS2"
    assert sample.tmd_fraction == 20
    assert sample.fraction_basis == FractionBasis.WEIGHT_PERCENT


def test_experimental_sample_rejects_negative_fraction():
    with pytest.raises(ValidationError):
        ExperimentalSample(
            sample_id="SMP-000001",
            paper_id="PPR-000001",
            psk=PSKDescription(
                formula_reported="CaTiO3",
            ),
            tmd=TMDDescription(
                formula_reported="MoS2",
            ),
            tmd_fraction=-10,
        )


# ---------------------------------------------------------------------------
# SAMPLE SERIES
# ---------------------------------------------------------------------------
def test_valid_sample_series():
    series = SampleSeries(
        sample_series_id="SER-000001",
        paper_id="PPR-000001",
        pair_id="PAIR-000001",
        series_name_reported="MoS2/CaTiO3 loading series",
    )

    assert series.sample_series_id == "SER-000001"
    assert series.paper_id == "PPR-000001"
    assert series.pair_id == "PAIR-000001"


def test_experimental_sample_can_belong_to_series():
    sample = ExperimentalSample(
        sample_id="SMP-000001",
        paper_id="PPR-000001",
        sample_series_id="SER-000001",
        psk=PSKDescription(
            formula_reported="CaTiO3",
        ),
        tmd=TMDDescription(
            formula_reported="MoS2",
        ),
    )

    assert sample.sample_series_id == "SER-000001"


def test_mechanism_assessment_can_apply_to_series():
    assessment = MechanismAssessment(
        mechanism_assessment_id="MEA-000001",
        sample_id="SMP-000001",
        applies_to_series_id="SER-000001",
        mechanism_normalized=MechanismLabel.Z_SCHEME,
        charge_transfer_class=(
            ChargeTransferClass.MEDIATED_RECOMBINATION
        ),
    )

    assert assessment.sample_id == "SMP-000001"
    assert assessment.applies_to_series_id == "SER-000001"


# ---------------------------------------------------------------------------
# SYNTHESIS
# ---------------------------------------------------------------------------
def test_valid_synthesis_record():
    record = SynthesisRecord(
        synthesis_id="SYN-000001",
        sample_id="SMP-000001",
        topology=SynthesisTopology.PSK_FIRST_TWO_STAGE,
        method_reported="in-situ hydrothermal",
    )

    assert record.synthesis_id == "SYN-000001"
    assert record.sample_id == "SMP-000001"
    assert record.topology == SynthesisTopology.PSK_FIRST_TWO_STAGE
    assert record.method_reported == "in-situ hydrothermal"


def test_synthesis_record_defaults_to_unknown_topology():
    record = SynthesisRecord(
        synthesis_id="SYN-000001",
        sample_id="SMP-000001",
    )

    assert record.topology == SynthesisTopology.UNKNOWN


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER MECHANISM
# ---------------------------------------------------------------------------
def test_mechanism_assessment_valid():
    assessment = MechanismAssessment(
        mechanism_assessment_id="MEA-000001",
        sample_id="SMP-000001",
        mechanism_reported="S-scheme",
        mechanism_normalized=MechanismLabel.S_SCHEME,
        charge_transfer_class=ChargeTransferClass.MEDIATED_RECOMBINATION,
        assessment_confidence=0.9,
        label_status=LabelStatus.ACCEPTED,
    )

    assert assessment.mechanism_normalized == MechanismLabel.S_SCHEME
    assert (
        assessment.charge_transfer_class
        == ChargeTransferClass.MEDIATED_RECOMBINATION
    )
    assert assessment.assessment_confidence == 0.9


def test_mechanism_assessment_rejects_confidence_above_one():
    with pytest.raises(ValidationError):
        MechanismAssessment(
            mechanism_assessment_id="MEA-000001",
            sample_id="SMP-000001",
            assessment_confidence=1.1,
        )


def test_mechanism_assessment_does_not_auto_map_label():
    assessment = MechanismAssessment(
        mechanism_assessment_id="MEA-000001",
        sample_id="SMP-000001",
        mechanism_normalized=MechanismLabel.Z_SCHEME,
    )

    assert assessment.charge_transfer_class is None


# ---------------------------------------------------------------------------
# MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def test_mechanism_evidence_valid():
    evidence = MechanismEvidence(
        evidence_id="EVD-000001",
        mechanism_assessment_id="MEA-000001",
        evidence_type=EvidenceType.XPS,
        support=EvidenceSupport.SUPPORTS,
        evidence_strength=EvidenceStrength.MODERATE,
        reported_result=(
            "Binding-energy shifts indicate "
            "interfacial electron redistribution."
        ),
        source_location="Figure 6",
        characterization_role=(
            CharacterizationRole.MECHANISM_ASSESSMENT
        ),
        mechanism_discriminating=True,
        requires_context=True,
        required_context=[
            EvidenceContextType.BAND_ALIGNMENT,
        ],
        section_role=(
            PaperSectionRole.RESULTS
        ),
        section_title=(
            "Results and discussion"
        ),
        page_number=6,
    )

    assert (
        evidence.evidence_type
        == EvidenceType.XPS
    )

    assert (
        evidence.support
        == EvidenceSupport.SUPPORTS
    )

    assert (
        evidence.evidence_strength
        == EvidenceStrength.MODERATE
    )

    assert (
        evidence.characterization_role
        == CharacterizationRole.MECHANISM_ASSESSMENT
    )

    assert (
        evidence.mechanism_discriminating
        is True
    )

    assert (
        evidence.requires_context
        is True
    )

    assert (
        evidence.required_context
        == [
            EvidenceContextType.BAND_ALIGNMENT,
        ]
    )

    assert (
        evidence.section_role
        == PaperSectionRole.RESULTS
    )

    assert (
        evidence.section_title
        == "Results and discussion"
    )

    assert (
        evidence.page_number
        == 6
    )

    assert (
        evidence.source_location
        == "Figure 6"
    )


def test_mechanism_evidence_defaults():
    evidence = MechanismEvidence(
        evidence_id="EVD-000002",
        mechanism_assessment_id="MEA-000001",
    )

    assert (
        evidence.evidence_type
        == EvidenceType.UNKNOWN
    )

    assert (
        evidence.support
        == EvidenceSupport.UNKNOWN
    )

    assert (
        evidence.evidence_strength
        == EvidenceStrength.UNKNOWN
    )

    assert (
        evidence.characterization_role
        == CharacterizationRole.OTHER
    )

    assert (
        evidence.mechanism_discriminating
        is False
    )

    assert (
        evidence.requires_context
        is False
    )

    assert (
        evidence.required_context
        == []
    )

    assert (
        evidence.section_role
        == PaperSectionRole.OTHER
    )

    assert (
        evidence.section_title
        is None
    )

    assert (
        evidence.page_number
        is None
    )


def test_mechanism_evidence_context_required_valid():
    evidence = MechanismEvidence(
        evidence_id="EVD-000003",
        mechanism_assessment_id="MEA-000001",
        evidence_type=(
            EvidenceType.RADICAL_TRAPPING
        ),
        characterization_role=(
            CharacterizationRole.MECHANISM_ASSESSMENT
        ),
        mechanism_discriminating=True,
        requires_context=True,
        required_context=[
            EvidenceContextType.BAND_EDGES,
            EvidenceContextType.REDOX_POTENTIALS,
        ],
        section_role=(
            PaperSectionRole.MECHANISM
        ),
        section_title=(
            "Possible photocatalytic mechanism"
        ),
        page_number=9,
    )

    assert (
        evidence.requires_context
        is True
    )

    assert (
        EvidenceContextType.BAND_EDGES
        in evidence.required_context
    )

    assert (
        EvidenceContextType.REDOX_POTENTIALS
        in evidence.required_context
    )


def test_mechanism_evidence_requires_context_cannot_be_empty():
    with pytest.raises(
        ValidationError,
        match=(
            "Evidence requiring context "
            "must specify required_context"
        ),
    ):
        MechanismEvidence(
            evidence_id="EVD-000004",
            mechanism_assessment_id=(
                "MEA-000001"
            ),
            evidence_type=(
                EvidenceType.RADICAL_TRAPPING
            ),
            characterization_role=(
                CharacterizationRole.MECHANISM_ASSESSMENT
            ),
            mechanism_discriminating=True,
            requires_context=True,
            required_context=[],
        )


def test_mechanism_evidence_context_must_be_empty_when_not_required():
    with pytest.raises(
        ValidationError,
        match=(
            "required_context must be empty "
            "when requires_context is False"
        ),
    ):
        MechanismEvidence(
            evidence_id="EVD-000005",
            mechanism_assessment_id=(
                "MEA-000001"
            ),
            evidence_type=(
                EvidenceType.MOTT_SCHOTTKY
            ),
            characterization_role=(
                CharacterizationRole.BAND_STRUCTURE
            ),
            mechanism_discriminating=False,
            requires_context=False,
            required_context=[
                EvidenceContextType.BAND_EDGES,
            ],
        )


def test_mechanism_evidence_page_number_must_be_positive():
    with pytest.raises(
        ValidationError,
    ):
        MechanismEvidence(
            evidence_id="EVD-000006",
            mechanism_assessment_id=(
                "MEA-000001"
            ),
            page_number=0,
        )


def test_mechanism_evidence_band_structure_valid():
    evidence = MechanismEvidence(
        evidence_id="EVD-000007",
        mechanism_assessment_id="MEA-000001",
        evidence_type=(
            EvidenceType.MOTT_SCHOTTKY
        ),
        characterization_role=(
            CharacterizationRole.BAND_STRUCTURE
        ),
        mechanism_discriminating=False,
        requires_context=False,
        required_context=[],
        reported_result=(
            "Mott-Schottky analysis was used "
            "to determine flat-band potentials."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
        page_number=6,
    )

    assert (
        evidence.characterization_role
        == CharacterizationRole.BAND_STRUCTURE
    )

    assert (
        evidence.mechanism_discriminating
        is False
    )

    assert (
        evidence.requires_context
        is False
    )

    assert (
        evidence.required_context
        == []
    )


def test_mechanism_evidence_charge_separation_support_valid():
    evidence = MechanismEvidence(
        evidence_id="EVD-000008",
        mechanism_assessment_id="MEA-000001",
        evidence_type=(
            EvidenceType.UNKNOWN
        ),
        evidence_subtype=(
            "photoluminescence"
        ),
        characterization_role=(
            CharacterizationRole.CHARGE_SEPARATION_SUPPORT
        ),
        mechanism_discriminating=False,
        requires_context=False,
        required_context=[],
        reported_result=(
            "Lower PL intensity indicates "
            "reduced electron-hole recombination."
        ),
        section_role=(
            PaperSectionRole.RESULTS
        ),
        page_number=6,
    )

    assert (
        evidence.evidence_type
        == EvidenceType.UNKNOWN
    )

    assert (
        evidence.evidence_subtype
        == "photoluminescence"
    )

    assert (
        evidence.characterization_role
        == CharacterizationRole.CHARGE_SEPARATION_SUPPORT
    )

    assert (
        evidence.mechanism_discriminating
        is False
    )

    assert (
        evidence.requires_context
        is False
    )

    assert (
        evidence.required_context
        == []
    )


# ---------------------------------------------------------------------------
# PHOTOCATALYTIC TESTS
# ---------------------------------------------------------------------------
def test_general_photocatalytic_test_valid():
    test = PhotocatalyticTest(
        test_id="TST-000001",
        sample_id="SMP-000001",
        application_type=PhotocatalyticApplication.DYE_DEGRADATION,
        reaction_type="photocatalytic degradation",
        target_species="methylene blue",
        initial_target_concentration_value=10.0,
        initial_target_concentration_unit="mg/L",
        light_source="500 W Xe lamp",
        light_intensity_value=30000.0,
        light_intensity_unit="lux",
        catalyst_mass_mg=100.0,
        solution_volume_ml=100.0,
        dark_equilibration_time_min=30.0,
        test_duration_h=2.0,
        performance_metric_name="degradation efficiency",
        performance_metric_value=92.5,
        performance_metric_unit="%",
    )

    assert (
        test.application_type
        == PhotocatalyticApplication.DYE_DEGRADATION
    )
    assert test.target_species == "methylene blue"
    assert test.initial_target_concentration_value == 10.0
    assert test.initial_target_concentration_unit == "mg/L"
    assert test.light_intensity_value == 30000.0
    assert test.light_intensity_unit == "lux"
    assert test.dark_equilibration_time_min == 30.0
    assert test.performance_metric_value == 92.5


def test_hydrogen_evolution_test_valid():
    test = PhotocatalyticTest(
        test_id="TST-000002",
        sample_id="SMP-000001",
        application_type=PhotocatalyticApplication.HYDROGEN_EVOLUTION,
        reaction_type="photocatalytic hydrogen evolution",
        target_species="H2",
        performance_metric_name="hydrogen evolution rate",
        performance_metric_value=1250.0,
        performance_metric_unit="umol g-1 h-1",
    )

    assert (
        test.application_type
        == PhotocatalyticApplication.HYDROGEN_EVOLUTION
    )
    assert test.target_species == "H2"
    assert test.performance_metric_name == "hydrogen evolution rate"
    assert test.performance_metric_value == 1250.0
    assert test.performance_metric_unit == "umol g-1 h-1"


def test_photocatalytic_test_accepts_wavelength_cutoff():
    test = PhotocatalyticTest(
        test_id="TST-000003",
        sample_id="SMP-000001",
        wavelength_min_nm=420.0,
        visible_light_only=True,
    )

    assert test.wavelength_nm is None
    assert test.wavelength_min_nm == 420.0
    assert test.wavelength_max_nm is None
    assert test.visible_light_only is True


def test_photocatalytic_test_accepts_cycle_performance():
    test = PhotocatalyticTest(
        test_id="TST-000004",
        sample_id="SMP-000001",
        cycles=5,
        first_cycle_performance=91.12,
        last_cycle_performance=88.5,
    )

    assert test.cycles == 5
    assert test.first_cycle_performance == 91.12
    assert test.last_cycle_performance == 88.5


def test_photocatalytic_test_rejects_negative_concentration():
    with pytest.raises(ValidationError):
        PhotocatalyticTest(
            test_id="TST-000001",
            sample_id="SMP-000001",
            initial_target_concentration_value=-1.0,
        )


def test_photocatalytic_test_rejects_negative_light_intensity():
    with pytest.raises(ValidationError):
        PhotocatalyticTest(
            test_id="TST-000001",
            sample_id="SMP-000001",
            light_intensity_value=-1.0,
        )


def test_photocatalytic_test_rejects_zero_cycles():
    with pytest.raises(ValidationError):
        PhotocatalyticTest(
            test_id="TST-000001",
            sample_id="SMP-000001",
            cycles=0,
        )


# ---------------------------------------------------------------------------
# EXTRACTION RECORDS
# ---------------------------------------------------------------------------
def test_extraction_record_valid():
    record = ExtractionRecord(
        extraction_id="EXT-0001",
        paper_id="PPR-0001",
        target_table="photocatalytic_tests",
        target_record_id="TST-0001",
        target_field="test_duration_h",
        extractor_type=ExtractorType.MANUAL,
        source_location="Section 2.4",
        raw_value="120 min",
        normalized_value="2.0 h",
        confidence=0.95,
        manual_verified=True,
    )

    assert record.target_table == "photocatalytic_tests"
    assert record.target_record_id == "TST-0001"
    assert record.target_field == "test_duration_h"
    assert record.manual_verified is True


def test_extraction_record_rejects_invalid_confidence():
    with pytest.raises(ValidationError):
        ExtractionRecord(
            extraction_id="EXT-000001",
            paper_id="PPR-000001",
            confidence=-0.1,
        )


# ---------------------------------------------------------------------------
# EXTRACTION RECORD
# ---------------------------------------------------------------------------
def test_extraction_record_defaults_to_unknown_provenance_operation():
    record = ExtractionRecord(
        extraction_id="EXT-000001",
        paper_id="PPR-000001",
    )

    assert (
        record.provenance_operation
        == ProvenanceOperation.UNKNOWN
    )


def test_extraction_record_accepts_provenance_operation():
    record = ExtractionRecord(
        extraction_id="EXT-000001",
        paper_id="PPR-000001",
        provenance_operation=ProvenanceOperation.UNIT_NORMALIZATION,
        raw_value="120 min",
        normalized_value="2.0 h",
    )

    assert (
        record.provenance_operation
        == ProvenanceOperation.UNIT_NORMALIZATION
    )


# ---------------------------------------------------------------------------
# DISAGREEMENT RECORD
# ---------------------------------------------------------------------------
def test_valid_disagreement_record():
    record = DisagreementRecord(
        disagreement_id="DSG-000001",
        disagreement_type=DisagreementType.WITHIN_PAPER,
        status=DisagreementStatus.CURATOR_RESOLVED,
        paper_ids=["PPR-000004"],
        target_table="photocatalytic_tests",
        target_record_ids=["TST-000009"],
        target_field="performance_metric_value",
        reported_values=[
            "more than 96%",
            "91.12%",
        ],
        selected_value="91.12%",
    )

    assert record.disagreement_type == DisagreementType.WITHIN_PAPER
    assert record.status == DisagreementStatus.CURATOR_RESOLVED
    assert record.selected_value == "91.12%"


def test_disagreement_record_requires_reported_value():
    with pytest.raises(ValidationError):
        DisagreementRecord(
            disagreement_id="DSG-000001",
            disagreement_type=DisagreementType.WITHIN_PAPER,
            reported_values=[],
        )


# ---------------------------------------------------------------------------
# VALID PAIR MECHANISM LABEL
# ---------------------------------------------------------------------------
def test_valid_pair_mechanism_label():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
        source_assessment_ids=[
            "MEA-0001",
        ],
        mechanism_normalized=(
            MechanismLabel.Z_SCHEME
        ),
        charge_transfer_class=(
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        ),
        has_disagreement=False,
    )

    assert (
        label.pair_id
        == "PAIR-0001"
    )

    assert (
        label.source_assessment_ids
        == [
            "MEA-0001"
        ]
    )

    assert (
        label.mechanism_normalized
        == MechanismLabel.Z_SCHEME
    )

    assert (
        label.charge_transfer_class
        == (
            ChargeTransferClass
            .MEDIATED_RECOMBINATION
        )
    )

    assert (
        label.has_disagreement
        is False
    )


# ---------------------------------------------------------------------------
# PAIR LABEL DEFAULTS TO PENDING REVIEW
# ---------------------------------------------------------------------------
def test_pair_mechanism_label_defaults_to_pending_review():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
    )

    assert (
        label.manual_review_status
        == ManualReviewStatus.PENDING
    )

    assert (
        label.label_status
        == LabelStatus.PENDING_REVIEW
    )

    assert (
        label.mechanism_normalized
        is None
    )

    assert (
        label.charge_transfer_class
        is None
    )


# ---------------------------------------------------------------------------
# PAIR LABEL CAN PRESERVE DISAGREEMENT
# ---------------------------------------------------------------------------
def test_pair_mechanism_label_can_preserve_disagreement():
    label = PairMechanismLabel(
        pair_id="PAIR-0001",
        source_assessment_ids=[
            "MEA-0001",
            "MEA-0002",
        ],
        mechanism_normalized=None,
        charge_transfer_class=None,
        has_disagreement=True,
    )

    assert (
        label.has_disagreement
        is True
    )

    assert (
        label.mechanism_normalized
        is None
    )

    assert (
        label.charge_transfer_class
        is None
    )

