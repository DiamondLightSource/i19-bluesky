import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)

from i19_bluesky.serial.diffractometer_plans import move_stage_x_and_z


@pytest.mark.parametrize("detector_x,detector_z", [(200, 0), (100, 30), (80, 90)])
async def test_move_stage_x_and_z(
    detector_x: float,
    detector_z: float,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(move_stage_x_and_z(detector_x, detector_z, eh2_diffractometer))
    assert await eh2_diffractometer.x.user_readback.get_value() == detector_x
    assert await eh2_diffractometer.z.user_readback.get_value() == detector_z
