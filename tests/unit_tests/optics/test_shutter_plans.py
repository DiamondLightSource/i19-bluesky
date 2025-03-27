import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_optics
from dodal.devices.hutch_shutter import (
    HUTCH_SAFE_FOR_OPERATIONS,
    HutchShutter,
    ShutterDemand,
    ShutterState,
)
from dodal.devices.i19.hutch_access import HutchAccessControl
from dodal.utils import AnyDeviceFactory
from ophyd_async.testing import callback_on_mock_put, set_mock_value

from i19_bluesky.exceptions import HutchInvalidError
from i19_bluesky.optics.check_access_control import HutchName
from i19_bluesky.optics.experiment_shutter_plans import (
    operate_shutter_plan,
)
from tests.conftest import device_factories_for_beamline


@pytest.fixture(scope="session")
def active_device_factories() -> set[AnyDeviceFactory]:
    return device_factories_for_beamline(i19_optics)


@pytest.fixture
def expt_shutter(RE) -> HutchShutter:
    expt_shutter = i19_optics.shutter(connect_immediately=True, mock=True)
    set_mock_value(expt_shutter.interlock.status, HUTCH_SAFE_FOR_OPERATIONS)

    def set_status(value: ShutterDemand, *args, **kwargs):
        value_sta = ShutterState.OPEN if value == "Open" else ShutterState.CLOSED
        set_mock_value(expt_shutter.status, value_sta)

    callback_on_mock_put(expt_shutter.control, set_status)
    return expt_shutter


@pytest.fixture
def access_control_device(RE) -> HutchAccessControl:
    access_control = i19_optics.access_control(connect_immediately=True, mock=True)
    return access_control


@pytest.mark.parametrize(
    "active_hutch, request_hutch, shutter_demand, start_state, expected_state",
    [
        (
            "EH1",
            HutchName.EH1,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.OPEN,
        ),
        (
            "EH1",
            HutchName.EH1,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.CLOSED,
        ),
        (
            "EH2",
            HutchName.EH2,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.OPEN,
        ),
        (
            "EH2",
            HutchName.EH2,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.CLOSED,
        ),
    ],
)
async def test_hutch_shutter_opens_and_closes_if_run_by_active_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    start_state: ShutterState,
    expected_state: ShutterState,
    shutter_demand: ShutterDemand,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(expt_shutter.status, start_state)
    RE(
        operate_shutter_plan(
            request_hutch, access_control_device, shutter_demand, expt_shutter
        )
    )

    assert await expt_shutter.status.get_value() == expected_state


@pytest.mark.parametrize(
    "active_hutch, request_hutch, shutter_demand, start_state, expected_state",
    [
        (
            "EH1",
            HutchName.EH2,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.CLOSED,
        ),
        (
            "EH1",
            HutchName.EH2,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.OPEN,
        ),
        (
            "EH2",
            HutchName.EH1,
            ShutterDemand.OPEN,
            ShutterState.CLOSED,
            ShutterState.CLOSED,
        ),
        (
            "EH2",
            HutchName.EH1,
            ShutterDemand.CLOSE,
            ShutterState.OPEN,
            ShutterState.OPEN,
        ),
    ],
)
async def test_hutch_shutter_does_not_operate_from_wrong_hutch(
    active_hutch: str,
    request_hutch: HutchName,
    shutter_demand: ShutterDemand,
    start_state: ShutterState,
    expected_state: ShutterState,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, active_hutch)
    set_mock_value(expt_shutter.status, start_state)
    RE(
        operate_shutter_plan(
            request_hutch,
            access_control_device,
            shutter_demand,
            expt_shutter,
        )
    )

    assert await expt_shutter.status.get_value() == expected_state


@pytest.mark.parametrize(
    "request_hutch, shutter_demand",
    [
        (HutchName.EH1, ShutterDemand.OPEN),
        (HutchName.EH2, ShutterDemand.CLOSE),
    ],
)
def test_operate_hutch_shutter_raises_error_if_hutch_invalid(
    request_hutch: HutchName,
    shutter_demand: ShutterDemand,
    expt_shutter: HutchShutter,
    access_control_device: HutchAccessControl,
    RE: RunEngine,
):
    set_mock_value(access_control_device.active_hutch, "INVALID")
    with pytest.raises(HutchInvalidError):
        RE(
            operate_shutter_plan(
                request_hutch, access_control_device, shutter_demand, expt_shutter
            )
        )
