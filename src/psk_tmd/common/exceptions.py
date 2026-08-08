class PSKTMDException(Exception):
    """Base exception for all project-specific errors."""


class CorpusError(PSKTMDException):
    """Base exception for corpus-processing errors."""


class MaterialsError(PSKTMDException):
    """Base exception for MP/CMR and materials-data errors."""


class MappingError(PSKTMDException):
    """Base exception for mapping-related errors."""


class ModelingError(PSKTMDException):
    """Base exception for machine-learning pipeline errors."""
