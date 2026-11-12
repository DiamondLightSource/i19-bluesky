import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
    FocusingMirrorName,
)
from dodal.devices.beamlines.i19.access_controlled.shutter import (
    HutchState,
)
from dodal.devices.cryostream import OxfordCryoStream
from dodal.devices.oav.beam_centre.centroid_from_epics import CentroidFromEpics
from ophyd_async.core import set_mock_value


@pytest.fixture
async def cryostream(RE: RunEngine) -> OxfordCryoStream:
    cryo = OxfordCryoStream("", name="mock-cryo")
    await cryo.connect(mock=True)
    return cryo


@pytest.fixture
async def centroid_device(RE: RunEngine) -> CentroidFromEpics:
    device = CentroidFromEpics("", name="mock_centroid")
    await device.connect(mock=True)
    set_mock_value(device.beam_centre_x, 706)
    set_mock_value(device.beam_centre_y, 283)
    set_mock_value(device.cam_port_name, "OAV1.cam")
    set_mock_value(device.cc_port_name, "OAV1.cc")
    return device


@pytest.fixture
async def eh1_hfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    hfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorName.HFM, HutchState.EH1, "", "mock_hfm_piezo"
    )
    await hfm_piezo.connect(mock=True)
    hfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(hfm_piezo.readback, 5.236)
    return hfm_piezo


@pytest.fixture
async def eh2_vfm_piezo(RE: RunEngine) -> AccessControlledPiezoActuator:
    vfm_piezo = AccessControlledPiezoActuator(
        "", FocusingMirrorName.VFM, HutchState.EH2, "", "mock_vfm_piezo"
    )
    await vfm_piezo.connect(mock=True)
    vfm_piezo.url = "http://test-blueapi.url"
    set_mock_value(vfm_piezo.readback, 0.849)
    return vfm_piezo
