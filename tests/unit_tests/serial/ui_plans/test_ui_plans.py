import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.motors import XYZPhiStage
from ophyd_async.core import set_mock_value

from i19_bluesky.serial.ui_plans.ui_plans import (
    BacklightOption,
    move_backlight_in_via_ui,
    rotate_in_phi,
)


@pytest.mark.parametrize(
    "option, expected_det_z, expected_two_theta",
    [(BacklightOption.SLOW, 250, 90), (BacklightOption.QUICK, 100, 0)],
)
async def test_move_backlight_in_via_ui(
    option: BacklightOption,
    expected_det_z: float,
    expected_two_theta: float,
    RE: RunEngine,
    eh2_backlight: BacklightPosition,
    eh2_diffractometer: FourCircleDiffractometer,
):
    RE(move_backlight_in_via_ui(option, eh2_backlight, eh2_diffractometer))

    assert (
        await eh2_diffractometer.det_stage.det_z.user_readback.get_value()
        == expected_det_z
    )
    assert (
        await eh2_diffractometer.det_stage.two_theta.user_readback.get_value()
        == expected_two_theta
    )
    assert await eh2_backlight.position.get_value() == "IN"


@pytest.mark.parametrize(
    "rot_start, rot_increment, expected_end",
    [
        (-90.0, 10.0, -80.0),
        (0.0, -5.0, -5.0),
        (20.0, 4.0, 24.0),
    ],
)
async def test_rotate_in_phi(
    rot_start: float,
    rot_increment: float,
    expected_end: float,
    serial_stages: XYZPhiStage,
    RE: RunEngine,
):
    set_mock_value(serial_stages.phi.user_readback, rot_start)

    RE(rotate_in_phi(rot_increment, serial_stages))

    assert await serial_stages.phi.user_readback.get_value() == expected_end
