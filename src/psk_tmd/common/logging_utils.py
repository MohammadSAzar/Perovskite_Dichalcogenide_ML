import logging

from pathlib import Path


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


def setup_logging(
        level: int = logging.INFO,
        log_file: str | Path | None = None,
    ) -> None:
    """
    Configure project-wide logging.

    Parameters
    ----------
    level:
        Minimum logging level to display or record.
    log_file:
        Optional path to a log file. If None, logs are written only
        to the terminal.
    """

    handlers: list[logging.Handler] = [
        logging.StreamHandler()
    ]

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handlers.append(
            logging.FileHandler(
                log_path,
                encoding="utf-8",
            )
        )

    logging.basicConfig(
        level=level,
        format=DEFAULT_LOG_FORMAT,
        handlers=handlers,
        force=True,
    )

