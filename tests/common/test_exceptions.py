from psk_tmd.common.exceptions import (
    CorpusError,
    MappingError,
    MaterialsError,
    ModelingError,
    PSKTMDException,
)


def test_project_exceptions_inherit_from_base_exception():
    assert issubclass(CorpusError, PSKTMDException)
    assert issubclass(MaterialsError, PSKTMDException)
    assert issubclass(MappingError, PSKTMDException)
    assert issubclass(ModelingError, PSKTMDException)


def test_project_exception_can_be_raised_and_caught():
    try:
        raise CorpusError("Example corpus error")
    except PSKTMDException as exc:
        assert str(exc) == "Example corpus error"

