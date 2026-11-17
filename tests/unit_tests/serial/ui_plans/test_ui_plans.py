import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer

from i19_bluesky.serial.ui_plans.ui_plans import (
    BacklightOption,
    move_backlight_in_via_ui,
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
