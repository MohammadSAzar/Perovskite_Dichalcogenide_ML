from enum import Enum


# ---------------------------------------------------------------------------
# MATERIAL IDENTITY
# ---------------------------------------------------------------------------
class MaterialType(str, Enum):
    PSK = "PSK"
    TMD = "TMD"


class DataSource(str, Enum):
    MP = "MP"
    CMR = "CMR"


# ---------------------------------------------------------------------------
# CHARGE-TRANSFER LABELS
# ---------------------------------------------------------------------------
class ChargeTransferClass(str, Enum):
    MEDIATED_RECOMBINATION = "mediated_recombination"
    NON_MEDIATED_RECOMBINATION = "non_mediated_recombination"
    UNKNOWN = "unknown"


class MechanismLabel(str, Enum):
    Z_SCHEME = "z_scheme"
    S_SCHEME = "s_scheme"
    TYPE_II = "type_ii"
    SCHOTTKY = "schottky"
    P_N = "p_n"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# LITERATURE ACCESS AND DOCUMENT STATUS
# ---------------------------------------------------------------------------
class AccessType(str, Enum):
    OPEN_ACCESS = "open_access"
    INSTITUTIONAL_ACCESS = "institutional_access"
    REPOSITORY = "repository"
    AUTHOR_MANUSCRIPT = "author_manuscript"
    METADATA_ONLY = "metadata_only"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# EXPERIMENTAL SAMPLE METADATA
# ---------------------------------------------------------------------------
class FractionBasis(str, Enum):
    WEIGHT_PERCENT = "weight_percent"
    MOLE_PERCENT = "mole_percent"
    MASS_RATIO = "mass_ratio"
    MOLAR_RATIO = "molar_ratio"
    VOLUME_PERCENT = "volume_percent"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# SYNTHESIS
# ---------------------------------------------------------------------------
class SynthesisStepRole(str, Enum):
    PSK = "psk"
    TMD = "tmd"
    INTEGRATION = "integration"
    SIMULTANEOUS = "simultaneous"
    OTHER = "other"
    UNKNOWN = "unknown"


class SynthesisTopology(str, Enum):
    THREE_STAGE = "three_stage"
    PSK_FIRST_TWO_STAGE = "psk_first_two_stage"
    TMD_FIRST_TWO_STAGE = "tmd_first_two_stage"
    ONE_POT = "one_pot"
    COMMERCIAL_COMPONENT = "commercial_component"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# MECHANISM ASSESSMENT AND EVIDENCE
# ---------------------------------------------------------------------------
class LabelStatus(str, Enum):
    ACCEPTED = "accepted"
    UNCERTAIN = "uncertain"
    EXCLUDED = "excluded"
    PENDING_REVIEW = "pending_review"


class ManualReviewStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    NEEDS_REVIEW = "needs_review"


class EvidenceSupport(str, Enum):
    SUPPORTS = "supports"
    DOES_NOT_SUPPORT = "does_not_support"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"


class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    UNKNOWN = "unknown"


class EvidenceType(str, Enum):
    XPS = "xps"
    UPS = "ups"
    PL = "pl"
    ESR = "esr"
    RADICAL_TRAPPING = "radical_trapping"
    MOTT_SCHOTTKY = "mott_schottky"
    PHOTODEPOSITION = "photodeposition"
    PHOTOCURRENT = "photocurrent"
    CV = "cv"
    DFT = "dft"
    BAND_ALIGNMENT = "band_alignment"
    WORK_FUNCTION = "work_function"
    KELVIN_PROBE = "kelvin_probe"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# PHOTOCATALYTIC APPLICATIONS
# ---------------------------------------------------------------------------
class PhotocatalyticApplication(str, Enum):
    WATER_SPLITTING = "water_splitting"
    HYDROGEN_EVOLUTION = "hydrogen_evolution"
    POLLUTANT_DEGRADATION = "pollutant_degradation"
    DYE_DEGRADATION = "dye_degradation"
    ANTIBIOTIC_DEGRADATION = "antibiotic_degradation"
    CO2_REDUCTION = "co2_reduction"
    NITROGEN_FIXATION = "nitrogen_fixation"
    PHOTOELECTROCATALYSIS = "photoelectrocatalysis"
    PHOTO_ASSISTED_CATALYSIS = "photo_assisted_catalysis"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# EXTRACTION AND PROVENANCE
# ---------------------------------------------------------------------------
class ExtractorType(str, Enum):
    MANUAL = "manual"
    REGEX = "regex"
    NLP = "nlp"
    LLM = "llm"
    OTHER = "other"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# MATERIAL MAPPING
# ---------------------------------------------------------------------------
class MappingStatus(str, Enum):
    EXACT = "exact"
    PROBABLE = "probable"
    COMPOSITION_ONLY = "composition_only"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"
    NO_MATCH = "no_match"


