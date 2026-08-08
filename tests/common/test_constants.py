from psk_tmd.common.constants import (
    ChargeTransferClass,
    DataSource,
    MappingStatus,
    MaterialType,
    MechanismLabel,
)


def test_material_types():
    assert MaterialType.PSK.value == "PSK"
    assert MaterialType.TMD.value == "TMD"


def test_data_sources():
    assert DataSource.MP.value == "MP"
    assert DataSource.CMR.value == "CMR"


def test_mechanism_labels():
    assert MechanismLabel.Z_SCHEME.value == "z_scheme"
    assert MechanismLabel.S_SCHEME.value == "s_scheme"


def test_charge_transfer_classes():
    assert (
        ChargeTransferClass.MEDIATED_RECOMBINATION.value
        == "mediated_recombination"
    )


def test_mapping_status():
    assert MappingStatus.AMBIGUOUS.value == "ambiguous"

