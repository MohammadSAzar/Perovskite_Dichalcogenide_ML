import pytest

from pydantic import ValidationError

from psk_tmd.common.constants import (
    ChargeTransferClass,
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    FractionBasis,
    LabelStatus,
    MechanismLabel,
    PhotocatalyticApplication,
    SynthesisStepRole,
    ExtractorType,
)
from psk_tmd.common.models import (
    ExperimentalSample,
    ExtractionRecord,
    HeterostructureDescription,
    MechanismAssessment,
    MechanismEvidence,
    PaperRecord,
    PhotocatalyticTest,
    PSKDescription,
    SynthesisStep,
    TMDDescription,
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
# SYNTHESIS
# ---------------------------------------------------------------------------
def test_synthesis_step_valid():
    step = SynthesisStep(
        synthesis_step_id="SYN-000001",
        sample_id="SMP-000001",
        step_order=1,
        step_role=SynthesisStepRole.PSK,
        method="sol-gel",
        temperature_c=80,
        time_h=4,
    )

    assert step.step_order == 1
    assert step.method == "sol-gel"


def test_synthesis_step_rejects_zero_step_order():
    with pytest.raises(ValidationError):
        SynthesisStep(
            synthesis_step_id="SYN-000001",
            sample_id="SMP-000001",
            step_order=0,
        )


def test_synthesis_step_rejects_negative_time():
    with pytest.raises(ValidationError):
        SynthesisStep(
            synthesis_step_id="SYN-000001",
            sample_id="SMP-000001",
            step_order=1,
            time_h=-2,
        )


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

    assert assessment.charge_transfer_class == ChargeTransferClass.UNKNOWN


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
        source_location="Figure 6",
    )

    assert evidence.evidence_type == EvidenceType.XPS
    assert evidence.support == EvidenceSupport.SUPPORTS
    assert evidence.source_location == "Figure 6"


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
        performance_metric_name="degradation efficiency",
        performance_metric_value=92.5,
        performance_metric_unit="%",
    )

    assert (
        test.application_type
        == PhotocatalyticApplication.DYE_DEGRADATION
    )
    assert test.target_species == "methylene blue"
    assert test.performance_metric_value == 92.5


def test_hydrogen_evolution_test_valid():
    test = PhotocatalyticTest(
        test_id="TST-000002",
        sample_id="SMP-000001",
        application_type=PhotocatalyticApplication.HYDROGEN_EVOLUTION,
        hydrogen_rate_reported_value=1250,
        hydrogen_rate_reported_unit="umol g-1 h-1",
        hydrogen_rate_standardized_umol_g_h=1250,
    )

    assert test.hydrogen_rate_standardized_umol_g_h == 1250


def test_photocatalytic_test_rejects_negative_hydrogen_rate():
    with pytest.raises(ValidationError):
        PhotocatalyticTest(
            test_id="TST-000001",
            sample_id="SMP-000001",
            hydrogen_rate_standardized_umol_g_h=-1,
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


