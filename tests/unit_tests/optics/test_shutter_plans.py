import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_1
from dodal.devices.hutch_shutter import (
    HUTCH_SAFE_FOR_OPERATIONS,
    ShutterDemand,
    ShutterState,
)
from dodal.devices.i19.shutter import HutchConditionalShutter, HutchState
from dodal.utils import AnyDeviceFactory
from ophyd_async.testing import callback_on_mock_put, set_mock_value

from i19_bluesky.optics.experiment_shutter_plans import (
    close_hutch_shutter,
    open_hutch_shutter,
)
from tests.conftest import device_factories_for_beamline


@pytest.fixture(scope="session")
def active_device_factories() -> set[AnyDeviceFactory]:
    return device_factories_for_beamline(i19_1)


@pytest.fixture
def expt_shutter(RE) -> HutchConditionalShutter:
    expt_shutter = i19_1.shutter(connect_immediately=True, mock=True)
    set_mock_value(expt_shutter.shutter.interlock.status, HUTCH_SAFE_FOR_OPERATIONS)
    set_mock_value(expt_shutter.hutch_state, HutchState.EH1)

    def set_status(value: ShutterDemand, *args, **kwargs):
        value_sta = ShutterState.OPEN if value == "Open" else ShutterState.CLOSED
        set_mock_value(expt_shutter.shutter.status, value_sta)

    callback_on_mock_put(expt_shutter.shutter.control, set_status)
    return expt_shutter


async def test_open_and_close_hutch_shutter(
    expt_shutter: HutchConditionalShutter, RE: RunEngine
):
    RE(open_hutch_shutter(expt_shutter))
    assert await expt_shutter.shutter.status.get_value() == ShutterState.OPEN

    RE(close_hutch_shutter(expt_shutter))
    assert await expt_shutter.shutter.status.get_value() == ShutterState.CLOSED


async def test_if_wrong_hutch_shutter_does_not_move(
    expt_shutter: HutchConditionalShutter, RE: RunEngine
):
    set_mock_value(expt_shutter.hutch_state, HutchState.EH2)
    set_mock_value(expt_shutter.shutter.status, ShutterState.CLOSED)

    RE(open_hutch_shutter(expt_shutter))

    assert await expt_shutter.shutter.status.get_value() == ShutterState.CLOSED
