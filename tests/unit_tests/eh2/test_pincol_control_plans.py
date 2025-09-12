from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine
from dodal.devices.i19.pin_col_stages import PinColRequest, PinholeCollimatorControl

from i19_bluesky.eh2.pincol_control_plans import (
    move_pin_col_out_of_beam,
    move_pin_col_to_requested_in_position,
)


@patch("i19_bluesky.eh2.pincol_control_plans.bps.abs_set")
async def test_move_pincol_out(
    mock_set: MagicMock, pincol: PinholeCollimatorControl, RE: RunEngine
):
    RE(move_pin_col_out_of_beam(pincol))

    mock_set.assert_called_once_with(pincol, "OUT", wait=True)


@patch("i19_bluesky.eh2.pincol_control_plans.bps.abs_set")
async def test_move_pincol_in(
    mock_set: MagicMock, pincol: PinholeCollimatorControl, RE: RunEngine
):
    RE(move_pin_col_to_requested_in_position(PinColRequest.PCOL3000, pincol))

    mock_set.assert_called_once_with(pincol, PinColRequest.PCOL3000, wait=True)
