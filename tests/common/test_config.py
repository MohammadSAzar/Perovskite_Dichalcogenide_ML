from psk_tmd.common.config import (
    DATA_DIR,
    PROJECT_ROOT,
    RESULTS_DIR,
)


def test_project_root_exists():
    assert PROJECT_ROOT.exists()


def test_data_directory_exists():
    assert DATA_DIR.exists()


def test_results_directory_exists():
    assert RESULTS_DIR.exists()

