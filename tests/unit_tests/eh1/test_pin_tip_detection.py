from unittest.mock import AsyncMock, MagicMock, patch

import bluesky.plan_stubs as bps
import numpy as np
import pytest
from bluesky import RunEngine
from dodal.devices.i19.pin_tip import PinTipCentreHolder
from dodal.devices.oav.pin_image_recognition import PinTipDetection
from dodal.devices.oav.pin_image_recognition.utils import SampleLocation
from ophyd_async.core import init_devices

from i19_bluesky.eh1.pin_tip_detection import (
    pin_tip_detection_plan,
    save_pin_tip_position,
    trigger_pin_tip_detection,
)


@pytest.fixture
def pin_tip_detection(RE: RunEngine) -> PinTipDetection:
    with init_devices(mock=True):
        device = PinTipDetection("", "mock-pintip-detection")
    return device


@pytest.fixture
def pin_tip_position(RE: RunEngine) -> PinTipCentreHolder:
    with init_devices(mock=True):
        device = PinTipCentreHolder("", "mock-pintip-position")
    return device


async def test_save_pin_tip_position(
    pin_tip_position: PinTipCentreHolder, RE: RunEngine
):
    RE(save_pin_tip_position(pin_tip_position, np.array([10, 3])))

    assert await pin_tip_position.pin_tip_i.get_value() == 10
    assert await pin_tip_position.pin_tip_j.get_value() == 3


def test_trigger_pin_tip_detection_plan(
    pin_tip_detection: PinTipDetection, RE: RunEngine
):
    mock_trigger_result = SampleLocation(100, 200, np.array([]), np.array([]))
    pin_tip_detection._get_tip_and_edge_data = AsyncMock(
        return_value=mock_trigger_result
    )

    plan_res = RE(trigger_pin_tip_detection(pin_tip_detection)).plan_result  # type: ignore

    assert all(plan_res == (100, 200))


@patch("i19_bluesky.eh1.pin_tip_detection.setup_pin_tip_detection_params")
@patch("i19_bluesky.eh1.pin_tip_detection.trigger_pin_tip_detection")
@patch("i19_bluesky.eh1.pin_tip_detection.save_pin_tip_position")
def test_pin_tip_detection(
    mock_save_pos: MagicMock,
    mock_trigger_pin_tip: MagicMock,
    mock_setup_params: MagicMock,
    pin_tip_detection: PinTipDetection,
    pin_tip_position: PinTipCentreHolder,
    RE: RunEngine,
):
    def mock_pin_tip_generator(x, y):
        yield from bps.null()
        return np.array([x, y])

    mock_trigger_pin_tip.side_effect = [mock_pin_tip_generator(100, 50)]
    with patch(
        "i19_bluesky.eh1.pin_tip_detection.OAVParameters"  #
    ) as mock_params:
        RE(
            pin_tip_detection_plan(
                "someContext", pin_tip_detection, pin_tip_position, ""
            )
        )

        mock_setup_params.assert_called_once_with(
            pin_tip_detection, mock_params("someContext", "")
        )
        mock_trigger_pin_tip.assert_called_once()
        mock_save_pos.assert_called_once()
