import logging

from psk_tmd.common.logging_utils import setup_logging


# setup_logging()
setup_logging(
    log_file="results/logs/demo.log"
)

logger = logging.getLogger(__name__)

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")

