import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    DetectorMotion,
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
    well_x: float,
    well_z: float,
    diffractometer: FourCircleDiffractometer,
):
    """Moves the sample stage a distance of well_x and well_z in the respective\
                directions. Order dependant on position of detector when \
                called.
        Args:
            well_x : Float
                Distance to move in X axis
            well_z : Float
                Distance to move in Z axis
            diffractometer : FourCircleDiffractometer object
    """
    yield from bps.mv(diffractometer.x, well_x)
    yield from bps.mv(diffractometer.z, well_z)


def move_detector_stage(
    detector_stage: DetectorMotion, det_z: float, two_theta: float = 0.0
):
    """Moves the Detector a distance of det_z and two_theta in the respective\
                directions. Order dependant on position of detector when \
                called.
        Args:
            detector_stage : DetectorMotion object
            det_z : Float
                Distance to move in Z axis
            two_theta : Float
                (default 0.0)
                Distance to move in Two-Theta axis
    """
    current_location = yield from bps.rd(detector_stage.det_z)
    if current_location >= det_z:
        # if the current value is higher than the requested one, first attempt to move
        # 2theta and then det_z
        yield from bps.mv(detector_stage.two_theta, two_theta)
        yield from bps.mv(detector_stage.det_z, det_z)
    else:
        # otherwise first move det_z and then 2theta
        yield from bps.mv(detector_stage.det_z, det_z)
        yield from bps.mv(detector_stage.two_theta, two_theta)
