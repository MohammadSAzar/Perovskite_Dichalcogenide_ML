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
    SynthesisTopology,
    ProvenanceOperation,
    DisagreementType,
    DisagreementStatus,
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
    assert ChargeTransferClass.TYPE_I.value == "type_i"
    assert ChargeTransferClass.TYPE_II.value == "type_ii"
    assert ChargeTransferClass.TYPE_III.value == "type_iii"
    assert ChargeTransferClass.PN.value == "pn"
    assert ChargeTransferClass.SCHOTTKY.value == "schottky"


def test_mechanism_label_values():
    assert MechanismLabel.TYPE_I.value == "type_i"
    assert MechanismLabel.TYPE_II.value == "type_ii"
    assert MechanismLabel.TYPE_III.value == "type_iii"
    assert MechanismLabel.Z_SCHEME.value == "z_scheme"
    assert MechanismLabel.S_SCHEME.value == "s_scheme"
    assert MechanismLabel.SCHOTTKY.value == "schottky"
    assert MechanismLabel.P_N.value == "p_n"
    assert MechanismLabel.OTHER.value == "other"
    assert MechanismLabel.UNKNOWN.value == "unknown"


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
    assert EvidenceType.UPS.value == "ups"
    assert EvidenceType.PL.value == "pl"
    assert EvidenceType.ESR.value == "esr"
    assert EvidenceType.RADICAL_TRAPPING.value == "radical_trapping"
    assert EvidenceType.MOTT_SCHOTTKY.value == "mott_schottky"
    assert EvidenceType.PHOTODEPOSITION.value == "photodeposition"
    assert EvidenceType.PHOTOCURRENT.value == "photocurrent"
    assert EvidenceType.SPM.value == "spm"
    assert EvidenceType.EIS.value == "eis"
    assert EvidenceType.CV.value == "cv"
    assert EvidenceType.LSV.value == "lsv"
    assert EvidenceType.DFT.value == "dft"
    assert EvidenceType.BAND_ALIGNMENT.value == "band_alignment"
    assert EvidenceType.WORK_FUNCTION.value == "work_function"
    assert EvidenceType.KELVIN_PROBE.value == "kelvin_probe"
    assert EvidenceType.OTHER.value == "other"
    assert EvidenceType.UNKNOWN.value == "unknown"


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


# ---------------------------------------------------------------------------
# PROVENANCE OPERATION
# ---------------------------------------------------------------------------
def test_provenance_operation_values():
    assert (
        ProvenanceOperation.DIRECT_EXTRACTION.value
        == "direct_extraction"
    )
    assert (
        ProvenanceOperation.UNIT_NORMALIZATION.value
        == "unit_normalization"
    )
    assert (
        ProvenanceOperation.SEMANTIC_NORMALIZATION.value
        == "semantic_normalization"
    )
    assert (
        ProvenanceOperation.ONTOLOGY_MAPPING.value
        == "ontology_mapping"
    )
    assert (
        ProvenanceOperation.DERIVED_CALCULATION.value
        == "derived_calculation"
    )
    assert (
        ProvenanceOperation.CONFLICT_RESOLUTION.value
        == "conflict_resolution"
    )
    assert ProvenanceOperation.OTHER.value == "other"
    assert ProvenanceOperation.UNKNOWN.value == "unknown"


# ---------------------------------------------------------------------------
# DISAGREEMENT VALUES
# ---------------------------------------------------------------------------
def test_disagreement_type_values():
    assert DisagreementType.WITHIN_PAPER.value == "within_paper"
    assert DisagreementType.BETWEEN_PAPERS.value == "between_papers"
    assert DisagreementType.OTHER.value == "other"


def test_disagreement_status_values():
    assert DisagreementStatus.UNRESOLVED.value == "unresolved"
    assert (
        DisagreementStatus.CURATOR_RESOLVED.value
        == "curator_resolved"
    )
    assert DisagreementStatus.SOURCE_ERROR.value == "source_error"

