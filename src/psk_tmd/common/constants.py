from enum import Enum


class MaterialType(str, Enum):
    PSK = "PSK"
    TMD = "TMD"


class DataSource(str, Enum):
    MP = "MP"
    CMR = "CMR"


class ChargeTransferClass(str, Enum):
    MEDIATED_RECOMBINATION = "mediated_recombination"
    NON_MEDIATED_RECOMBINATION = "non_mediated_recombination"
    UNKNOWN = "unknown"


class MechanismLabel(str, Enum):
    Z_SCHEME = "z_scheme"
    S_SCHEME = "s_scheme"
    TYPE_II = "type_ii"
    OTHER = "other"
    UNKNOWN = "unknown"


class MappingStatus(str, Enum):
    EXACT = "exact"
    PROBABLE = "probable"
    COMPOSITION_ONLY = "composition_only"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"
    NO_MATCH = "no_match"

