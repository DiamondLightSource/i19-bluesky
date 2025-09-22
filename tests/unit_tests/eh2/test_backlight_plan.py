from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.common.enums import InOutUpper
from dodal.devices.i19.backlight import BacklightPosition

from i19_bluesky.eh2.backlight_plan import (
    move_backlight_in,
    move_backlight_out,
)


@patch("i19_bluesky.eh2.backlight_plan.bps.abs_set")
async def test_backlight_in_plan(
    mock_set: MagicMock, eh2_backlight: BacklightPosition, RE: RunEngine
):
    RE(move_backlight_in(eh2_backlight))

    mock_set.assert_called_once_with(eh2_backlight, InOutUpper.IN, wait=True)


@patch("i19_bluesky.eh2.backlight_plan.bps.abs_set")
async def test_backlight_out_plan(
    mock_set: MagicMock, eh2_backlight: BacklightPosition, RE: RunEngine
):
    RE(move_backlight_out(eh2_backlight))

    mock_set.assert_called_once_with(eh2_backlight, InOutUpper.OUT, wait=True)


@pytest.mark.parametrize(
    "position, specific_plan",
    [(InOutUpper.IN, move_backlight_in), (InOutUpper.OUT, move_backlight_out)],
)
async def test_backlight_position_plan(
    eh2_backlight: BacklightPosition, RE: RunEngine, position, specific_plan
):
    RE(specific_plan(eh2_backlight))
    await eh2_backlight.set(position)
    assert await eh2_backlight.position.get_value() == position
