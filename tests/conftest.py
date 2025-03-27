import logging
import os
import sys
from collections.abc import Sequence
from types import ModuleType
from typing import Any

import pytest
from dodal.log import LOGGER as dodal_logger
from dodal.utils import AnyDeviceFactory, collect_factories

from i19_bluesky.log import LOGGER, BeamlineHutch, do_default_logging_setup

TEST_GRAYLOG_PORT = 5555
TEST_HUTCH = BeamlineHutch.EH2

# Prevent pytest from catching exceptions when debugging in vscode so that break on
# exception works correctly (see: https://github.com/pytest-dev/pytest/issues/7409)
if os.getenv("PYTEST_RAISE", "0") == "1":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call: pytest.CallInfo[Any]):
        if call.excinfo is not None:
            raise call.excinfo.value
        else:
            raise RuntimeError(
                f"{call} has no exception data, an unknown error has occurred"
            )

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo: pytest.ExceptionInfo[Any]):
        raise excinfo.value


def device_factories_for_beamline(beamline_module: ModuleType) -> set[AnyDeviceFactory]:
    device_factories = collect_factories(beamline_module, include_skipped=True).values()
    return {f for f in device_factories if hasattr(f, "cache_clear")}


def _reset_loggers(loggers):
    """Clear all handlers and tear down the logging hierarchy, leave logger \
        references intact."""
    clear_log_handlers(loggers)
    for logger in loggers:
        if logger.name != "i19_bluesky":
            # Parent is configured on module import, do not remove
            logger.parent = logging.getLogger()


def clear_log_handlers(loggers: Sequence[logging.Logger]):
    for logger in loggers:
        for handler in logger.handlers:
            handler.close()
        logger.handlers.clear()


def pytest_runtest_setup(item):
    markers = [m.name for m in item.own_markers]
    if "skip_log_setup" not in markers:
        if LOGGER.handlers == []:
            if dodal_logger.handlers == []:
                print("Initialising I19 logger logger for tests")
                do_default_logging_setup(
                    "dev_log.py", TEST_HUTCH, TEST_GRAYLOG_PORT, dev_mode=True
                )
    else:
        print("Skipping log setup for log test - deleting existing handlers")
        _reset_loggers([LOGGER, dodal_logger])


def pytest_runtest_teardown(item):
    if "dodal.common.beamlines.beamline_utils" in sys.modules:
        sys.modules["dodal.common.beamlines.beamline_utils"].clear_devices()
    markers = [m.name for m in item.own_markers]
    if "skip_log_setup" in markers:
        _reset_loggers([LOGGER, dodal_logger])
