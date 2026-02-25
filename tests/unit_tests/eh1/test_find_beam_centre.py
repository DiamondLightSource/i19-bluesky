from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from bluesky import RunEngine
from dodal.devices.oav.beam_centre.beam_centre import CentreEllipseMethod
from ophyd_async.core import init_devices, set_mock_value

from i19_bluesky.eh1.find_beam_centre import find_beam_centre_plan


@pytest.fixture
async def centre_device() -> CentreEllipseMethod:
    async with init_devices(mock=True):
        centre_device = CentreEllipseMethod("TEST: ELLIPSE_CENTRE")
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    set_mock_value(centre_device.oav_array_signal, dummy_img)
    return centre_device


@patch("i19_bluesky.eh1.find_beam_centre_plan.bps.trigger")
async def test_find_beam_centre_plan(
    mock_trigger: MagicMock, centre_device: CentreEllipseMethod, RE: RunEngine
):
    RE(find_beam_centre_plan(centre_device))

    assert await centre_device.roi_box_size.get_value() == 10000
    mock_trigger.assert_called_once()
