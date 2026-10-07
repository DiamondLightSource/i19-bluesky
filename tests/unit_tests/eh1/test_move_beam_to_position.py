from unittest.mock import MagicMock, call, patch

import pytest
from bluesky import RunEngine
from dodal.devices.beamlines.i19.access_controlled.piezo_control import (
    AccessControlledPiezoActuator,
)
from dodal.devices.oav.beam_centre.centroid_from_epics import CentroidFromEpics
from ophyd_async.core import set_mock_value

from i19_bluesky.eh1.move_beam_to_position import (
    _calculate_nudge_from_lut,
    _check_position_reached,
    _get_lut_path_and_column_from_name,
    _read_current_position,
    nudge_hfm_and_move_beam_to_position,
    nudge_piezos_and_move_to_beam_centre,
    nudge_single_piezo,
    nudge_vfm_and_move_beam_to_position,
    setup_centroid_device,
    stop_stats_at_end,
)
from tests.unit_tests.conftest import fake_generator

TEST_HFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [-33.4, -8.35, 8.36, 33.8],
    [0.02, 0.04, 0.03, -0.09],
]
TEST_VFM_LUT_COLUMNS = [
    [-0.04, -0.01, 0.01, 0.04],
    [1.82, 0.45, -0.46, -1.86],
    [-37.67, -9.38, 9.33, 37.3],
]


async def test_read_current_position(centroid_device: CentroidFromEpics, RE: RunEngine):
    set_mock_value(centroid_device.beam_centre_x, 710)
    set_mock_value(centroid_device.beam_centre_y, 253)

    (beam_x, beam_y) = RE(_read_current_position(centroid_device)).plan_result  # type: ignore

    assert await centroid_device.beam_centre_x.get_value() == beam_x
    assert await centroid_device.beam_centre_y.get_value() == beam_y


@pytest.mark.parametrize(
    "device_name, expected_idx, expected_filename",
    [
        ("hfm_piezo", 1, "hfm_nudge_to_position.txt"),
        ("vfm_piezo", 2, "vfm_nudge_to_position.txt"),
    ],
)
def test_get_lut_path_and_column_from_name(
    device_name: str, expected_idx: int, expected_filename: str
):
    filepath, idx = _get_lut_path_and_column_from_name(device_name)

    assert idx == expected_idx
    assert filepath.name == expected_filename


def test_get_lut_path_and_column_from_name_fails_for_unexpected_device():
    with pytest.raises(ValueError):
        _get_lut_path_and_column_from_name("beam_centre")


@pytest.mark.parametrize(
    "device_name, test_lut, distance, expected_nudge",
    [
        ("hfm_piezo", TEST_HFM_LUT_COLUMNS, 10, 0.012),
        ("vfm_piezo", TEST_VFM_LUT_COLUMNS, 20, 0.021),
    ],
)
@patch("i19_bluesky.eh1.move_beam_to_position._read_lut")
def test_calculate_nudge_from_lut(
    mock_lut_columns: MagicMock,
    device_name: str,
    test_lut: list,
    distance: float,
    expected_nudge: float,
):
    mock_lut_columns.return_value = test_lut
    nudge_size = _calculate_nudge_from_lut(distance, device_name)

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


async def test_setup_centroid_device(centroid_device: CentroidFromEpics, RE: RunEngine):
    RE(setup_centroid_device(centroid_device))

    assert await centroid_device.stats.nd_array_port.get_value() == "OAV1.cc"
    assert await centroid_device.stats.centroid_threshold.get_value() == 20
    assert await centroid_device.colour_mode.get_value() == "Mono"
    assert await centroid_device.stats.enable_callbacks.get_value() == "Enable"
    assert await centroid_device.stats.compute_centroid.get_value() is True


async def test_stop_stats_at_end(centroid_device: CentroidFromEpics, RE: RunEngine):
    RE(stop_stats_at_end(centroid_device))

    assert await centroid_device.stats.enable_callbacks.get_value() == "Disable"
    assert await centroid_device.stats.compute_statistics.get_value() is False
    assert await centroid_device.stats.compute_centroid.get_value() is False
    assert await centroid_device.stats.compute_profiles.get_value() is False
    assert await centroid_device.stats.compute_histogram.get_value() is False


@patch("i19_bluesky.eh1.move_beam_to_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.eh1.move_beam_to_position._calculate_nudge_from_lut")
async def test_nudge_single_piezo_hfm(
    mock_calc: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    set_mock_value(eh1_hfm_piezo.setpoint, 1.24)
    mock_calc.return_value = 0.02

    RE(nudge_single_piezo(16, eh1_hfm_piezo))

    mock_apply_voltage_plan.assert_called_once_with(1.26, eh1_hfm_piezo)


@patch("i19_bluesky.eh1.move_beam_to_position.apply_voltage_to_piezo_actuators")
@patch("i19_bluesky.eh1.move_beam_to_position._calculate_nudge_from_lut")
async def test_nudge_single_piezo_vfm(
    mock_calc: MagicMock,
    mock_apply_voltage_plan: MagicMock,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    set_mock_value(eh1_vfm_piezo.setpoint, 1.70)
    mock_calc.return_value = -0.01

    RE(nudge_single_piezo(-9, eh1_vfm_piezo))

    mock_apply_voltage_plan.assert_called_once_with(1.69, eh1_vfm_piezo)


@patch("i19_bluesky.eh1.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.eh1.move_beam_to_position._check_position_reached")
@patch("i19_bluesky.eh1.move_beam_to_position.nudge_single_piezo")
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


@patch("i19_bluesky.eh1.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.eh1.move_beam_to_position._check_position_reached")
@patch("i19_bluesky.eh1.move_beam_to_position.nudge_single_piezo")
async def test_nudge_piezos_and_move_to_beam_centre_stops_after_max_iterations(
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

    mock_check.side_effect = [False, False]

    RE(
        nudge_piezos_and_move_to_beam_centre(
            (710, 290), 1, eh1_hfm_piezo, eh1_vfm_piezo, centroid_device
        )
    )

    # Should only be called twice as only 1 iteration
    assert mock_sleep.call_count == 2
    assert mock_nudge.call_count == 2


@patch("i19_bluesky.eh1.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.eh1.move_beam_to_position._read_current_position")
@patch("i19_bluesky.eh1.move_beam_to_position.nudge_single_piezo")
async def test_nudge_hfm_and_move(
    mock_nudge: MagicMock,
    mock_read: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh1_hfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    # Two loops to reach position
    target_pos = (706, 250)
    mock_read.side_effect = [
        fake_generator((720, 390)),
        fake_generator((706.9, 390.5)),
        fake_generator((706.2, 390.54)),
    ]

    RE(nudge_hfm_and_move_beam_to_position(target_pos, eh1_hfm_piezo, centroid_device))

    assert mock_sleep.call_count == 2
    mock_nudge.assert_has_calls(
        [call(-14, eh1_hfm_piezo), call(pytest.approx(-0.9, abs=1e-2), eh1_hfm_piezo)],
        any_order=True,
    )


@patch("i19_bluesky.eh1.move_beam_to_position.bps.sleep")
@patch("i19_bluesky.eh1.move_beam_to_position._read_current_position")
@patch("i19_bluesky.eh1.move_beam_to_position.nudge_single_piezo")
async def test_nudge_vfm_and_move(
    mock_nudge: MagicMock,
    mock_read: MagicMock,
    mock_sleep: MagicMock,
    centroid_device: CentroidFromEpics,
    eh1_vfm_piezo: AccessControlledPiezoActuator,
    RE: RunEngine,
):
    # Oneloop to reach position
    target_pos = (706, 250)
    mock_read.side_effect = [
        fake_generator((707, 346.6)),
        fake_generator((707.4, 333.5)),
    ]

    RE(nudge_vfm_and_move_beam_to_position(target_pos, eh1_vfm_piezo, centroid_device))

    assert mock_sleep.call_count == 1
    mock_nudge.assert_has_calls(
        [call(pytest.approx(-13.27, abs=1e-2), eh1_vfm_piezo)], any_order=True
    )
