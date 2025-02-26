import os
from types import ModuleType
from typing import Any

import pytest
from dodal.utils import AnyDeviceFactory, collect_factories

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
