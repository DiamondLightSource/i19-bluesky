from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine

from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.ui_plans.ui_plans import (
    move_backlight_in_via_ui,
    move_backlight_in_via_ui_quick,
    rotate_in_phi,
)


@patch("i19_bluesky.serial.ui_plans.ui_plans.move_detector_stage")
@patch("i19_bluesky.serial.ui_plans.ui_plans.move_backlight_in")
async def test_move_backlight_in_via_ui_quick(
    mock_move_backlight_in: MagicMock,
    mock_move_detector_stage: MagicMock,
    RE: RunEngine,
    devices: DeviceInput,
):
    RE(move_backlight_in_via_ui_quick(devices))

    mock_move_detector_stage.assert_called_once_with(
        devices.diffractometer.det_stage, 100, 0
    )
    mock_move_backlight_in.assert_called_once_with(devices.backlight)


@patch("i19_bluesky.serial.ui_plans.ui_plans.move_detector_stage")
@patch("i19_bluesky.serial.ui_plans.ui_plans.move_backlight_in")
async def test_move_backlight_in_via_ui(
    mock_move_backlight_in: MagicMock,
    mock_move_detector_stage: MagicMock,
    RE: RunEngine,
    devices: DeviceInput,
):
    RE(move_backlight_in_via_ui(devices))
    mock_move_detector_stage.assert_called_once_with(
        devices.diffractometer.det_stage, 250, 90
    )
    mock_move_backlight_in.assert_called_once_with(devices.backlight)


@patch("i19_bluesky.serial.ui_plans.ui_plans.bps.abs_set")
async def test_rotate_in_phi(
    mock_abs_set: MagicMock,
    RE: RunEngine,
    parameters: SerialExperiment,
    devices: DeviceInput,
):
    parameters.rot_axis_end = 10
    RE(rotate_in_phi(parameters, devices))
    mock_abs_set.assert_called_once_with(devices.diffractometer.phi, 10, wait=True)
