import pytest
from dodal.beamlines import i19_optics
from dodal.devices.focusing_mirror import FocusingMirrorWithPiezo
from dodal.devices.hutch_shutter import (
    HUTCH_SAFE_FOR_OPERATIONS,
    HutchShutter,
    ShutterDemand,
    ShutterState,
)
from dodal.devices.i19.access_controlled.hutch_access import HutchAccessControl
from dodal.utils import AnyDeviceFactory
from ophyd_async.core import callback_on_mock_put, set_mock_value

from tests.conftest import device_factories_for_beamline


@pytest.fixture(scope="session")
def active_device_factories() -> set[AnyDeviceFactory]:
    return device_factories_for_beamline(i19_optics)


@pytest.fixture
def expt_shutter(RE) -> HutchShutter:
    expt_shutter = i19_optics.shutter.build(connect_immediately=True, mock=True)
    set_mock_value(expt_shutter.interlock.status, HUTCH_SAFE_FOR_OPERATIONS)

    def set_status(value: ShutterDemand, *args, **kwargs):
        value_sta = ShutterState.OPEN if value == "Open" else ShutterState.CLOSED
        set_mock_value(expt_shutter.status, value_sta)

    callback_on_mock_put(expt_shutter.control, set_status)
    return expt_shutter


@pytest.fixture
def access_control_device(RE) -> HutchAccessControl:
    access_control = i19_optics.access_control.build(
        connect_immediately=True, mock=True
    )
    return access_control


@pytest.fixture
def vfm(RE) -> FocusingMirrorWithPiezo:
    vfm = i19_optics.vfm.build(connect_immediately=True, mock=True)
    set_mock_value(vfm.piezo, 1.0)
    return vfm


@pytest.fixture
def hfm(RE) -> FocusingMirrorWithPiezo:
    hfm = i19_optics.hfm.build(connect_immediately=True, mock=True)
    set_mock_value(hfm.piezo, 3.0)
    return hfm
