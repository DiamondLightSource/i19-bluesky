import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
    FocusingMirrorType,
)
from dodal.devices.i19.access_controlled.shutter import (
    AccessControlledShutter,
    HutchState,
)
from ophyd_async.core import set_mock_value


@pytest.fixture
async def eh1_shutter(RE: RunEngine) -> AccessControlledShutter:
    shutter = AccessControlledShutter("", HutchState.EH1, name="mock_shutter")
    await shutter.connect(mock=True)

    shutter.url = "http://test-blueapi.url"
    return shutter


@pytest.fixture
async def eh1_hfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    hfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorType.HFM, HutchState.EH1, "", "mock_hfm_piezo"
    )
    await hfm_piezo.connect(mock=True)
    hfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(hfm_piezo.readback, 5.236)
    return hfm_piezo


@pytest.fixture
async def eh1_vfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    vfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorType.VFM, HutchState.EH1, "", "mock_hfm_piezo"
    )
    await vfm_piezo.connect(mock=True)
    vfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(vfm_piezo.readback, 0.849)
    return vfm_piezo
