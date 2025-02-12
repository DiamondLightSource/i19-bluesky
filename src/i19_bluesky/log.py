import logging
from os import environ
from pathlib import Path

from bluesky.log import logger as bluesky_logger
from dodal.log import (
    ERROR_LOG_BUFFER_LINES,
    DodalLogHandlers,
    set_up_all_logging_handlers,
)
from dodal.log import LOGGER as dodal_logger

LOGGER = logging.getLogger("i19_bluesky")
LOGGER.setLevel(logging.DEBUG)
LOGGER.parent = dodal_logger

# Temporarily duplicated https://github.com/bluesky/ophyd-async/issues/550
ophyd_async_logger = logging.getLogger("ophyd_async")


__logger_handlers: DodalLogHandlers | None = None


def _integrate_bluesky_logs(parent_logger: logging.Logger):
    """Include logs from bluesky and ophyd_async."""
    for log in [bluesky_logger, ophyd_async_logger]:
        log.parent = parent_logger
        log.setLevel(logging.DEBUG)


def _get_logging_path(hutch: str) -> Path:
    """Get the path to write the log files to.

    Args:
        hutch (str): Hutch currently running bluesky.

    Returns:
        logging_path (Path): Path to the log file for the file handler to write to.
    """
    beamline = environ.get("BEAMLINE")
    if not beamline:
        logging_path = Path(f"/tmp/logs/bluesky/{hutch}")
    else:
        logging_path = Path(f"/dls_sw/{hutch}/logs/bluesky")
    logging_path.mkdir(exist_ok=True, parents=True)
    return logging_path


def do_default_logging_setup(
    filename: Path | str,
    hutch: str,
    graylog_port: int | None,
    dev_mode: bool = False,
):
    """Configures dodal logger so that separate debug and info log files are created,
    info logs are sent to Graylog and streamed to sys.sterr."""
    handlers = set_up_all_logging_handlers(
        LOGGER,
        _get_logging_path(hutch),
        "dodal.log",
        dev_mode,
        ERROR_LOG_BUFFER_LINES,
        graylog_port,
    )

    global __logger_handlers
    __logger_handlers = handlers
