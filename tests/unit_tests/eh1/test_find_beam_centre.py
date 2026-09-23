from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from bluesky import RunEngine
from dodal.devices.oav.beam_centre.beam_centre import CentreEllipseMethod
from dodal.devices.oav.beam_centre.centroid_from_epics import (
    CentroidFromEpics,
)
from dodal.devices.oav.oav_detector import OAVBeamCentreFile
from ophyd_async.core import init_devices, set_mock_value

from i19_bluesky.eh1.find_beam_centre import (
    find_beam_centre_plan,
    setup_ad_plugin_chain_for_beam_centre,
)

from ..conftest import fake_generator


@pytest.fixture
async def centre_device() -> CentreEllipseMethod:
    async with init_devices(mock=True):
        centre_device = CentreEllipseMethod("TEST: ELLIPSE_CENTRE")
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    set_mock_value(centre_device.oav_array_signal, dummy_img)
    return centre_device


@pytest.fixture
async def oav() -> OAVBeamCentreFile:
    oav_config = MagicMock()
    async with init_devices(mock=True, connect=True):
        oav = OAVBeamCentreFile("", config=oav_config, name="oav")
    set_mock_value(oav.snapshot.x_size, 1024)
    set_mock_value(oav.snapshot.y_size, 768)
    return oav


@pytest.fixture
async def centroid_device() -> CentroidFromEpics:
    async with init_devices(mock=True):
        device = CentroidFromEpics("", name="test-centroid")
    set_mock_value(device.beam_centre_x, 1024)
    set_mock_value(device.beam_centre_y, 768)
    return device


@pytest.mark.parametrize(
    "image_size, expected_roi",
    [([768, 1024], 1024), ([1024, 1024], 1024), ([1292, 964], 1292)],
)
@patch("i19_bluesky.eh1.find_beam_centre.trigger_beam_centre_fit")
async def test_find_beam_centre_plan(
    mock_trigger_plan: MagicMock,
    image_size: list[int],
    expected_roi: int,
    centre_device: CentreEllipseMethod,
    oav: OAVBeamCentreFile,
    RE: RunEngine,
):
    set_mock_value(oav.snapshot.x_size, image_size[0])
    set_mock_value(oav.snapshot.y_size, image_size[1])

    mock_trigger_plan.side_effect = [fake_generator((757, 365))]

    RE(find_beam_centre_plan(centre_device, oav))

    assert await centre_device.roi_box_size.get_value() == expected_roi
    mock_trigger_plan.assert_called_once()


async def test_setup_ad_plugin_chain(centroid_device: CentroidFromEpics, RE: RunEngine):
    RE(setup_ad_plugin_chain_for_beam_centre(centroid_device))

    assert await centroid_device.cc_array_port.get_value() == "OAV1.cam"
    assert await centroid_device.stat_array_port.get_value() == "OAV1.cc"
    assert await centroid_device.colour_mode.get_value() == "Mono"  # B/W
    assert await centroid_device.centroid_threshold.get_value() == 20
