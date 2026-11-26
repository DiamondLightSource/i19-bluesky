from unittest.mock import MagicMock, call, patch

import pytest
from bluesky import RunEngine
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import CentroidFromEpics
from ophyd_async.core import set_mock_value

from i19_bluesky.plans.move_beam_to_position import (
    NudgeDirection,
    _calculate_nudge_from_lut,
    _check_position_reached,
    _read_current_position,
    nudge_and_move_in_one_direction,
    nudge_piezos_and_move_to_beam_centre,
    nudge_single_piezo,
)
from tests.unit_tests.conftest import fake_generator

TEST_HFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [-33.4, -8.35, 8.36, 33.8],
]
TEST_VFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [-37.67, -9.38, 9.33, 37.3],
]

TEST_LUT = [[0.01, 0.02], [8.361, 16.769], [0.035, -0.009]]


async def test_read_current_position(centroid_device: CentroidFromEpics, RE: RunEngine):
    set_mock_value(centroid_device.beam_centre_x, 710)
    set_mock_value(centroid_device.beam_centre_y, 253)

    (beam_x, beam_y) = RE(_read_current_position(centroid_device)).plan_result  # type: ignore

    assert await centroid_device.beam_centre_x.get_value() == beam_x
    assert await centroid_device.beam_centre_y.get_value() == beam_y


@pytest.mark.parametrize(
    "test_lut, distance, expected_nudge",
    [
        (TEST_HFM_LUT_COLUMNS, 10, 0.012),
        (TEST_VFM_LUT_COLUMNS, 20, 0.021),
    ],
)
def test_calculate_nudge_from_lut(
    test_lut: list,
    distance: float,
    expected_nudge: float,
):
    nudge_size = _calculate_nudge_from_lut(distance, test_lut)

    assert nudge_size == pytest.approx(expected_nudge, abs=1e-3)


@pytest.mark.parametrize(
    "position, target, expected_res",
    [
        ((690, 302), (710, 283), False),
        ((710.3, 284.9), (710, 283), False),
        ((712, 283.2), (710, 283), False),
        ((710.2, 283.4), (710, 283), True),
    ],
)
def test_check_position_reached(
    position: tuple[float, float],
    target: tuple[float, float],
    expected_res: bool,
):
    res = _check_position_reached(target, position)
    assert res == expected_res


@patch("i19_bluesky.plans.move_beam_to_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.plans.move_beam_to_position._calculate_nudge_from_lut")
async def test_nudge_single_piezo_hfm(
    mock_calc: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    eh1_hfm_piezo._read_lut = MagicMock(return_value=TEST_LUT)
    set_mock_value(eh1_hfm_piezo.setpoint, 1.24)
    mock_calc.return_value = 0.02

    RE(nudge_single_piezo(16, eh1_hfm_piezo))

    mock_apply_voltage_plan.assert_called_once_with(1.26, eh1_hfm_piezo)


@patch("i19_bluesky.plans.move_beam_to_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.plans.move_beam_to_position._calculate_nudge_from_lut")
async def test_nudge_single_piezo_vfm(
    mock_calc: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    eh2_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    eh2_vfm_piezo._read_lut = MagicMock(return_value=TEST_LUT)
    set_mock_value(eh2_vfm_piezo.setpoint, 1.70)
    mock_calc.return_value = -0.01

    RE(nudge_single_piezo(-9, eh2_vfm_piezo))

    mock_apply_voltage_plan.assert_called_once_with(1.69, eh2_vfm_piezo)


@patch("i19_bluesky.plans.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.plans.move_beam_to_position._check_position_reached")
@patch("i19_bluesky.plans.move_beam_to_position.nudge_single_piezo")
async def test_nudge_piezos_and_move_to_beam_centre(
    mock_nudge: MagicMock,
    mock_check: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    set_mock_value(centroid_device.beam_centre_x, 720)
    set_mock_value(centroid_device.beam_centre_y, 390.5)

    mock_check.side_effect = [False, True]

    RE(
        nudge_piezos_and_move_to_beam_centre(
            (710, 290), 5, eh1_hfm_piezo, eh1_vfm_piezo, centroid_device
        )
    )

    # Should only be called twice as second check returns True and loop ends
    mock_sleep.assert_has_calls([call(2.0), call(2.0)], any_order=True)
    mock_nudge.assert_has_calls(
        [
            call(pytest.approx(-3.833, abs=1e-3), eh1_vfm_piezo),
            call(-10, eh1_hfm_piezo),
        ],
        any_order=True,
    )


@patch("i19_bluesky.plans.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.plans.move_beam_to_position._check_position_reached")
@patch("i19_bluesky.plans.move_beam_to_position.nudge_single_piezo")
async def test_nudge_piezos_and_move_to_beam_centre_stops_after_max_iterations(
    mock_nudge: MagicMock,
    mock_check: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh2_hfm_piezo: AccessControlledPiezoActuator,
    eh2_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    set_mock_value(centroid_device.beam_centre_x, 720)
    set_mock_value(centroid_device.beam_centre_y, 390.5)

    mock_check.side_effect = [False, False]

    RE(
        nudge_piezos_and_move_to_beam_centre(
            (710, 290), 1, eh2_hfm_piezo, eh2_vfm_piezo, centroid_device
        )
    )

    # Should only be called twice as only 1 iteration
    assert mock_sleep.call_count == 2
    assert mock_nudge.call_count == 2


@patch("i19_bluesky.plans.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.plans.move_beam_to_position.bps.rd")
@patch("i19_bluesky.plans.move_beam_to_position.nudge_single_piezo")
async def test_nudge_and_move_in_one_direction_for_hfm(
    mock_nudge: MagicMock,
    mock_read: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    target_pos = 706
    mock_read.side_effect = [
        fake_generator(720),
        fake_generator(706.9),
        fake_generator(706.2),
    ]

    RE(
        nudge_and_move_in_one_direction(
            target_pos, NudgeDirection.X, eh1_hfm_piezo, centroid_device
        )
    )

    assert mock_sleep.call_count == 2
    mock_nudge.assert_has_calls(
        [call(-14, eh1_hfm_piezo), call(pytest.approx(-0.9, abs=1e-2), eh1_hfm_piezo)],
        any_order=True,
    )


@patch("i19_bluesky.plans.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.plans.move_beam_to_position.bps.rd")
@patch("i19_bluesky.plans.move_beam_to_position.nudge_single_piezo")
async def test_nudge_and_move_in_one_direction_for_vfm(
    mock_nudge: MagicMock,
    mock_read: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh2_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    # Oneloop to reach position
    target = 250
    mock_read.side_effect = [
        fake_generator(346.6),
        fake_generator(333.5),
    ]

    RE(
        nudge_and_move_in_one_direction(
            target, NudgeDirection.Y, eh2_vfm_piezo, centroid_device
        )
    )

    assert mock_sleep.call_count == 1
    mock_nudge.assert_has_calls(
        [call(pytest.approx(-13.27, abs=1e-2), eh2_vfm_piezo)], any_order=True
    )


@patch("i19_bluesky.plans.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.plans.move_beam_to_position.bps.rd")
@patch("i19_bluesky.plans.move_beam_to_position.nudge_single_piezo")
async def test_nudge_and_move_in_one_direction_for_vfm_reaches_max_tries_and_breaks(
    mock_nudge: MagicMock,
    mock_read: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh2_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    # Would need 11 loops to reach position
    target_pos = 250
    mock_read.side_effect = [
        fake_generator(365),
        fake_generator(351.1),
        fake_generator(349.6),
        fake_generator(346.6),
        fake_generator(342.6),
        fake_generator(340.2),
        fake_generator(338.6),
        fake_generator(336.1),
        fake_generator(335),
        fake_generator(334.2),
        fake_generator(333.9),
        fake_generator(333.5),
    ]
    RE(
        nudge_and_move_in_one_direction(
            target_pos, NudgeDirection.Y, eh2_vfm_piezo, centroid_device
        )
    )

    assert mock_sleep.call_count == 10
    assert mock_nudge.call_count == 10
