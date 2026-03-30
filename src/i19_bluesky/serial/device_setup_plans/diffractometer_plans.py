import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    DetectorMotion,
    FourCircleDiffractometer,
)

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.serial_parameters import SerialExperiment


def setup_diffractometer(
    parameters: SerialExperiment,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Setup phi start posistion and velocity on the diffractometer.

    Args:
        parameters (SerialExperiment): Parameters object containing:
            rot_axis_start (float): Starting phi position.
            images_per_well (int): Number of images to take.
            exposure_time_s (float): Time between images, in seconds.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
    """
    yield from bps.abs_set(diffractometer.phi, parameters["rot_axis_start"])
    velocity = parameters["images_per_well"] / parameters["exposure_time_s"]
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
    yield from bps.mv(diffractometer.x, well_x, diffractometer.z, well_z)


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
        yield from bps.abs_set(detector_stage.two_theta, two_theta, wait=True)
        yield from bps.abs_set(detector_stage.det_z, det_z, wait=True)
    else:
        # otherwise first move det_z and then 2theta
        yield from bps.abs_set(detector_stage.det_z, det_z, wait=True)
        yield from bps.abs_set(detector_stage.two_theta, two_theta, wait=True)
