import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)

from i19_bluesky.log import LOGGER


def setup_diffractometer(
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_steps: int,
    exposure_time: float,
) -> MsgGenerator:
    """Setup phi start posistion and velocity on the diffractometer.

    Args:
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position.
        phi_steps (int): Number of images to take.
        exposure_time(float): Time between images, in seconds."""
    yield from bps.abs_set(diffractometer.phi, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(diffractometer.phi.velocity, velocity)


def move_diffractometer_back(
    diffractometer: FourCircleDiffractometer, phi_start: float
) -> MsgGenerator:
    LOGGER.info("Move diffractometer back to start position")
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)


def move_stage_x_and_z(
    det_x: float,
    det_z: float,
    detector_stage: FourCircleDiffractometer,
):
    """Moves the Detector a distance of det_z and two_theta in the respective\
                directions. Order dependant on position of detector when \
                called.
        Args:
            det_x : Float
                Distance to move in X axis
            det_z : Float
                Distance to move in Z axis
            detector_stage : FourCircleDiffractometer object
    """
    yield from bps.mv(detector_stage.x, det_x)
    yield from bps.mv(detector_stage.det_stage.det_z, det_z)
