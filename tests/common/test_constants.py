from psk_tmd.common.constants import (
    AccessType,
    ChargeTransferClass,
    DataSource,
    EvidenceStrength,
    EvidenceSupport,
    EvidenceType,
    ExtractorType,
    FractionBasis,
    LabelStatus,
    ManualReviewStatus,
    MappingStatus,
    MaterialType,
    MechanismLabel,
    PhotocatalyticApplication,
    SynthesisStepRole,
    SynthesisTopology,
)


# ---------------------------------------------------------------------------
# MATERIAL IDENTITY
# ---------------------------------------------------------------------------
def test_material_type_values():
    assert MaterialType.PSK.value == "PSK"
    assert MaterialType.TMD.value == "TMD"


def test_data_source_values():
    assert DataSource.MP.value == "MP"
    assert DataSource.CMR.value == "CMR"


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER LABELS
# ---------------------------------------------------------------------------
def test_charge_transfer_class_values():
    assert (
        ChargeTransferClass.MEDIATED_RECOMBINATION.value
        == "mediated_recombination"
    )
    assert (
        ChargeTransferClass.NON_MEDIATED_RECOMBINATION.value
        == "non_mediated_recombination"
    )


def test_mechanism_label_values():
    assert MechanismLabel.Z_SCHEME.value == "z_scheme"
    assert MechanismLabel.S_SCHEME.value == "s_scheme"
    assert MechanismLabel.TYPE_II.value == "type_ii"
    assert MechanismLabel.SCHOTTKY.value == "schottky"
    assert MechanismLabel.P_N.value == "p_n"


# ---------------------------------------------------------------------------
# LITERATURE AND SAMPLE METADATA
# ---------------------------------------------------------------------------
def test_access_type_values():
    assert AccessType.OPEN_ACCESS.value == "open_access"
    assert AccessType.INSTITUTIONAL_ACCESS.value == "institutional_access"


def test_fraction_basis_values():
    assert FractionBasis.WEIGHT_PERCENT.value == "weight_percent"
    assert FractionBasis.MOLAR_RATIO.value == "molar_ratio"


# ---------------------------------------------------------------------------
# SYNTHESIS
# ---------------------------------------------------------------------------
def test_synthesis_step_role_values():
    assert SynthesisStepRole.PSK.value == "psk"
    assert SynthesisStepRole.TMD.value == "tmd"
    assert SynthesisStepRole.INTEGRATION.value == "integration"


def test_synthesis_topology_values():
    assert SynthesisTopology.THREE_STAGE.value == "three_stage"
    assert SynthesisTopology.ONE_POT.value == "one_pot"


# ---------------------------------------------------------------------------
# MECHANISM EVIDENCE
# ---------------------------------------------------------------------------
def test_label_status_values():
    assert LabelStatus.ACCEPTED.value == "accepted"
    assert LabelStatus.UNCERTAIN.value == "uncertain"


def test_manual_review_status_values():
    assert ManualReviewStatus.PENDING.value == "pending"
    assert ManualReviewStatus.REVIEWED.value == "reviewed"


def test_evidence_support_values():
    assert EvidenceSupport.SUPPORTS.value == "supports"
    assert EvidenceSupport.AMBIGUOUS.value == "ambiguous"


def test_evidence_strength_values():
    assert EvidenceStrength.STRONG.value == "strong"
    assert EvidenceStrength.WEAK.value == "weak"


def test_evidence_type_values():
    assert EvidenceType.XPS.value == "xps"
    assert EvidenceType.MOTT_SCHOTTKY.value == "mott_schottky"
    assert EvidenceType.DFT.value == "dft"


# ---------------------------------------------------------------------------
# PHOTOCATALYTIC APPLICATIONS
# ---------------------------------------------------------------------------
def test_photocatalytic_application_values():
    assert (
        PhotocatalyticApplication.WATER_SPLITTING.value
        == "water_splitting"
    )
    assert (
        PhotocatalyticApplication.POLLUTANT_DEGRADATION.value
        == "pollutant_degradation"
    )
    assert (
        PhotocatalyticApplication.PHOTOELECTROCATALYSIS.value
        == "photoelectrocatalysis"
    )


# ---------------------------------------------------------------------------
# EXTRACTION AND MAPPING
# ---------------------------------------------------------------------------
def test_extractor_type_values():
    assert ExtractorType.MANUAL.value == "manual"
    assert ExtractorType.LLM.value == "llm"


def test_mapping_status_values():
    assert MappingStatus.EXACT.value == "exact"
    assert MappingStatus.AMBIGUOUS.value == "ambiguous"
    assert MappingStatus.NO_MATCH.value == "no_match"


