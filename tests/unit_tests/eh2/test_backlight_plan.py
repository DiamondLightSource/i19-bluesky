from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.i19.backlight import BacklightPosition

from i19_bluesky.eh2.backlight_plan import (
    backlight_in,
    backlight_out,
)


@patch("i19_bluesky.eh2.backlight_plan.bps.abs_set")
async def test_backlight_in_plan(
    mock_set: MagicMock, eh2_backlight: BacklightPosition, RE: RunEngine
):
    RE(backlight_in(eh2_backlight))

    mock_set.assert_called_once_with(eh2_backlight, InOutUpper.IN, wait=True)


@patch("i19_bluesky.eh2.backlight_plan.bps.abs_set")
async def test_backlight_out_plan(
    mock_set: MagicMock, eh2_backlight: BacklightPosition, RE: RunEngine
):
    RE(backlight_out(eh2_backlight))

    mock_set.assert_called_once_with(eh2_backlight, InOutUpper.OUT, wait=True)
