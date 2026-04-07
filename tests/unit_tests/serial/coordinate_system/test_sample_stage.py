from bluesky import RunEngine
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from ophyd_async.core import set_mock_value

from i19_bluesky.serial.coordinate_system.sample_stage import (
    move_sample_stage_to_corners,
    read_current_sample_stage_xyz_position,
)


def test_read_current_xyz_position(
    eh2_diffractometer: FourCircleDiffractometer, RE: RunEngine
):
    set_mock_value(eh2_diffractometer.x.user_readback, 2.4)
    set_mock_value(eh2_diffractometer.y.user_readback, 0.0)
    set_mock_value(eh2_diffractometer.z.user_readback, 0.5)

    res = RE(read_current_sample_stage_xyz_position(eh2_diffractometer)).plan_result  # type: ignore

    assert res == (2.4, 0.0, 0.5)


async def test_move_sample_to_position(
    eh2_diffractometer: FourCircleDiffractometer, RE: RunEngine
):
    RE(move_sample_stage_to_corners((0.1, 1.2, 0.8), eh2_diffractometer))

    assert await eh2_diffractometer.x.user_readback.get_value() == 0.1
    assert await eh2_diffractometer.y.user_readback.get_value() == 1.2
    assert await eh2_diffractometer.z.user_readback.get_value() == 0.8
