from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.i19.pin_col_stages import PinColRequest, PinholeCollimatorControl
from ophyd_async.core import set_mock_value

from i19_bluesky.eh2.pincol_control_plans import (
    move_pin_col_out_of_beam,
    move_pin_col_to_requested_in_position,
)


@patch("i19_bluesky.eh2.pincol_control_plans.bps.abs_set")
async def test_move_pincol_out(
    mock_set: MagicMock, pincol: PinholeCollimatorControl, RE: RunEngine
):
    RE(move_pin_col_out_of_beam(pincol))

    mock_set.assert_called_once_with(pincol, PinColRequest.OUT, wait=True)


@patch("i19_bluesky.eh2.pincol_control_plans.bps.abs_set")
async def test_move_pincol_in(
    mock_set: MagicMock, pincol: PinholeCollimatorControl, RE: RunEngine
):
    RE(move_pin_col_to_requested_in_position(PinColRequest.PCOL3000, pincol))

    mock_set.assert_called_once_with(pincol, PinColRequest.PCOL3000, wait=True)


async def test_when_moving_pincol_out_stage_x_motors_actually_move(
    pincol: PinholeCollimatorControl, RE: RunEngine
):
    expected_out_position = [30.0, 20.0]
    set_mock_value(pincol._pinhole.x.user_readback, 20.3)
    set_mock_value(pincol._collimator.x.user_readback, 15)

    RE(move_pin_col_out_of_beam(pincol))

    assert await pincol._pinhole.x.user_readback.get_value() == expected_out_position[0]
    assert (
        await pincol._collimator.x.user_readback.get_value() == expected_out_position[1]
    )


@pytest.mark.parametrize(
    "aperture_request, in_positions",
    [
        (PinColRequest.PCOL20, [12, 34.5, 7.1, 28]),
        (PinColRequest.PCOL40, [15.2, 24, 10, 16]),
        (PinColRequest.PCOL100, [23.4, 22.1, 12, 18.7]),
        (PinColRequest.PCOL3000, [25, 18, 15.3, 20]),
    ],
)
async def test_when_moving_pincol_to_requested_aperture_all_motors_move_to_position(
    aperture_request: PinColRequest,
    in_positions: list[float],
    pincol: PinholeCollimatorControl,
    RE: RunEngine,
):
    size = int(aperture_request.value.strip("um"))
    set_mock_value(pincol.mapt.pin_x.in_positions[size], in_positions[0])
    set_mock_value(pincol.mapt.pin_y.in_positions[size], in_positions[1])
    set_mock_value(pincol.mapt.col_x.in_positions[size], in_positions[2])
    set_mock_value(pincol.mapt.col_y.in_positions[size], in_positions[3])

    RE(move_pin_col_to_requested_in_position(aperture_request, pincol))

    assert await pincol._pinhole.x.user_readback.get_value() == in_positions[0]
    assert await pincol._pinhole.y.user_readback.get_value() == in_positions[1]
    assert await pincol._collimator.x.user_readback.get_value() == in_positions[2]
    assert await pincol._collimator.y.user_readback.get_value() == in_positions[3]
