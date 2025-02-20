import logging
from enum import Enum
from os import environ
from pathlib import Path

from bluesky.log import logger as bluesky_logger
from dodal.log import (
    DEFAULT_GRAYLOG_PORT,
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


class BeamlineHutch(str, Enum):
    """Define the beamline name depending on hutch.
    Useful to get the path to save the logs."""

    EH1 = "i19-1"
    EH2 = "i19-2"


def integrate_bluesky_logs(parent_logger: logging.Logger):
    """Include logs from bluesky and ophyd_async."""
    for log in [bluesky_logger, ophyd_async_logger]:
        log.parent = parent_logger
        log.setLevel(logging.DEBUG)


def _get_logging_path(hutch: BeamlineHutch) -> Path:
    """Get the path to write the log files to.

    Args:
        hutch (BeamlineHutch): Hutch currently running bluesky.

    Returns:
        logging_path (Path): Path to the log file for the file handler to write to.
    """
    # NOTE Can't use the beamline variable as it's automatically set to
    # i19-1 on the beamline workstations even if running in i19-2.
    beamline = environ.get("BEAMLINE")
    if not beamline:
        logging_path = Path(f"/tmp/logs/bluesky/{hutch.value}")
    else:
        logging_path = Path(f"/dls_sw/{hutch.value}/logs/bluesky")
    logging_path.mkdir(exist_ok=True, parents=True)
    return logging_path


def do_default_logging_setup(
    filename: str,
    hutch: BeamlineHutch,
    graylog_port: int | None,
    dev_mode: bool = False,
):
    """Configures dodal logger so that separate debug and info log files are created,
    info logs are sent to Graylog and streamed to sys.sterr."""
    handlers = set_up_all_logging_handlers(
        dodal_logger,
        _get_logging_path(hutch),
        filename,
        dev_mode,
        ERROR_LOG_BUFFER_LINES,
        graylog_port,
    )

    global __logger_handlers
    __logger_handlers = handlers


def setup_log_config(hutch: BeamlineHutch, dev_mode: bool = False):
    """Configure the logging.

    Args:
        hutch (BeamlineHutch): Define which hutch is running the plans.
        dev_mode (bool, optional): If true, will log to graylog on localhost instead \
            of production. Defaults to False.
    """
    do_default_logging_setup(
        "i19-bluesky.log",
        hutch,
        DEFAULT_GRAYLOG_PORT,
        dev_mode,
    )
    integrate_bluesky_logs(dodal_logger)
