import pytest
from bluesky import RunEngine
from dodal.devices.i19.pin_tip import PinTipCentreHolder
from dodal.devices.oav.pin_image_recognition import PinTipDetection
from ophyd_async.core import init_devices

from i19_bluesky.eh1.pin_tip_detection import save_pin_tip_position


@pytest.fixture
def pin_tip_detection() -> PinTipDetection:
    with init_devices(mock=True):
        device = PinTipDetection("", "mock-pintip-detection")
    return device


@pytest.fixture
def pin_tip_position() -> PinTipCentreHolder:
    with init_devices(mock=True):
        device = PinTipCentreHolder("", "mock-pintip-position")
    return device


async def test_save_pin_tip_position(
    pin_tip_position: PinTipCentreHolder, RE: RunEngine
):
    RE(save_pin_tip_position(pin_tip_position, (10, 3)))

    assert await pin_tip_position.pin_tip_i.get_value() == 10
    assert await pin_tip_position.pin_tip_j.get_value() == 3
