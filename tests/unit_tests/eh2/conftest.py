import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i19_2
from dodal.devices.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
    FocusingMirrorType,
)
from dodal.devices.i19.access_controlled.shutter import (
    AccessControlledShutter,
    HutchState,
)
from dodal.devices.i19.backlight import BacklightPosition
from dodal.devices.i19.pin_col_stages import PinholeCollimatorControl
from ophyd_async.core import set_mock_value


@pytest.fixture
async def eh2_shutter(RE: RunEngine) -> AccessControlledShutter:
    shutter = AccessControlledShutter("", HutchState.EH2, name="mock_shutter")
    await shutter.connect(mock=True)

    shutter.url = "http://test-blueapi.url"
    return shutter


@pytest.fixture
async def pincol(RE: RunEngine) -> PinholeCollimatorControl:
    pincol = i19_2.pinhole_and_collimator.build(connect_immediately=True, mock=True)
    set_mock_value(pincol.mapt.pin_x_out, 30.0)
    set_mock_value(pincol.mapt.col_x_out, 20.0)
    return pincol


@pytest.fixture
async def eh2_backlight(RE: RunEngine) -> BacklightPosition:
    backlight = BacklightPosition("", name="mock_backlight")
    await backlight.connect(mock=True)
    return backlight


@pytest.fixture
async def eh2_hfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    hfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorType.HFM, HutchState.EH2, "", "mock_hfm_piezo"
    )
    await hfm_piezo.connect(mock=True)
    hfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(hfm_piezo.readback, 3.041)
    return hfm_piezo


@pytest.fixture
async def eh2_vfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    vfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorType.VFM, HutchState.EH2, "", "mock_hfm_piezo"
    )
    await vfm_piezo.connect(mock=True)
    vfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(vfm_piezo.readback, 1.675)
    return vfm_piezo
