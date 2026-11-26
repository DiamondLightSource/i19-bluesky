import pytest
from bluesky.run_engine import RunEngine
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
