import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.motors import XYZPhiStage

from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_stage_x_and_z,
)


@pytest.mark.parametrize("detector_x,detector_z", [(200, 0), (100, 30), (80, 90)])
async def test_move_stage_x_and_z(
    detector_x: float,
    detector_z: float,
    serial_stages: XYZPhiStage,
    RE: RunEngine,
):
    RE(move_stage_x_and_z(detector_x, detector_z, serial_stages))
    assert await serial_stages.x.user_readback.get_value() == detector_x
    assert await serial_stages.z.user_readback.get_value() == detector_z
