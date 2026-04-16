from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from ophyd_async.core import set_mock_value

from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.serial.ui_plans.ui_plans import (
    move_backlight_in_via_ui,
    rotate_in_phi,
)


@pytest.mark.parametrize(
    "param,det_z,two_theta",
    [
        ({"option": "slow"}, 250, 90),
        (
            {
                "option": "quick",
            },
            100,
            0,
        ),
        ({"option": "???"}, 0, 0),
    ],
)
@patch("i19_bluesky.serial.ui_plans.ui_plans.move_detector_stage")
@patch("i19_bluesky.serial.ui_plans.ui_plans.move_backlight_in")
async def test_move_backlight_in_via_ui(
    mock_move_backlight_in: MagicMock,
    mock_move_detector_stage: MagicMock,
    param: dict,
    det_z: float,
    two_theta: float,
    RE: RunEngine,
    devices: SerialCollectionEh2PandaComposite,
):
    RE(move_backlight_in_via_ui(param, devices))
    mock_move_detector_stage.assert_called_once_with(
        devices.diffractometer.det_stage, det_z, two_theta
    )
    mock_move_backlight_in.assert_called_once_with(devices.backlight)


@pytest.mark.parametrize(
    "params",
    [
        ({"rot_axis_increment": 10.0}),
        ({"rot_axis_increment": 50.0}),
        ({"rot_axis_increment": -4.0}),
    ],
)
@patch("i19_bluesky.serial.ui_plans.ui_plans.bps.abs_set")
async def test_rotate_in_phi(
    mock_abs_set: MagicMock,
    RE: RunEngine,
    params: dict,
    devices: SerialCollectionEh2PandaComposite,
):

    rot_axis_end = (
        params["rot_axis_increment"] + 0
    )  # 0 = start position of diffractometer
    RE(rotate_in_phi(params, devices))
    mock_abs_set.assert_called_with(
        devices.diffractometer.phi,
        rot_axis_end,
        wait=True,
    )
    set_mock_value(devices.diffractometer.phi.user_readback, rot_axis_end)
    RE(rotate_in_phi(params, devices))
    mock_abs_set.assert_called_with(
        devices.diffractometer.phi, rot_axis_end + rot_axis_end, wait=True
    )
