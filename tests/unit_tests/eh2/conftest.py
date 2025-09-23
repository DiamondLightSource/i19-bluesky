from collections.abc import AsyncGenerator

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.devices.i19.backlight import BacklightPosition
from dodal.devices.i19.pin_col_stages import PinholeCollimatorControl
from dodal.devices.i19.shutter import AccessControlledShutter, HutchState
from dodal.devices.zebra.zebra import Zebra
from dodal.testing import patch_all_motors
from ophyd_async.testing import get_mock_put, set_mock_value


@pytest.fixture
async def eh2_shutter(RE: RunEngine) -> AccessControlledShutter:
    shutter = AccessControlledShutter("", HutchState.EH2, name="mock_shutter")
    await shutter.connect(mock=True)

    shutter.url = "http://test-blueapi.url"
    return shutter


@pytest.fixture
async def pincol(RE: RunEngine) -> AsyncGenerator[PinholeCollimatorControl]:
    pincol = i19_2.pincol(connect_immediately=True, mock=True)
    set_mock_value(pincol.mapt.pin_x_out, 30.0)
    set_mock_value(pincol.mapt.col_x_out, 20.0)
    with patch_all_motors(pincol):
        yield pincol


@pytest.fixture
def eh2_zebra(RE: RunEngine) -> Zebra:
    zebra = i19_2.zebra(connect_immediately=True, mock=True)

    def mock_disarm(_, wait):
        set_mock_value(zebra.pc.arm.armed, 0)

    def mock_arm(_, wait):
        set_mock_value(zebra.pc.arm.armed, 1)

    get_mock_put(zebra.pc.arm.arm_set).side_effect = mock_arm
    get_mock_put(zebra.pc.arm.disarm_set).side_effect = mock_disarm
    return zebra


@pytest.fixture
async def eh2_backlight(RE: RunEngine) -> BacklightPosition:
    backlight = BacklightPosition("", name="mock_backlight")
    await backlight.connect(mock=True)
    return backlight
