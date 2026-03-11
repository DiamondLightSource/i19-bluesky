import pytest
from bluesky.run_engine import RunEngine
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)

from i19_bluesky.serial.setup_detector import setup_detector


@pytest.mark.parametrize(
    "detector_z,detector_two_theta", [(200, 0), (100, 30), (80, 90)]
)
async def test_setup_detector(
    detector_z: float,
    detector_two_theta: float,
    eh2_diffractometer: FourCircleDiffractometer,
    RE: RunEngine,
):
    RE(setup_detector(eh2_diffractometer, detector_z, detector_two_theta))
    assert (
        await eh2_diffractometer.det_stage.det_z.user_readback.get_value() == detector_z
    )
    assert (
        await eh2_diffractometer.det_stage.two_theta.user_readback.get_value()
        == detector_two_theta
    )
