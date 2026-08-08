import logging

from psk_tmd.common.logging_utils import setup_logging


def test_setup_logging_sets_root_level():
    setup_logging(level=logging.DEBUG)

    root_logger = logging.getLogger()

    assert root_logger.level == logging.DEBUG

