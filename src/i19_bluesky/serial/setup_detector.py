from bluesky.log import logger
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer

import i19_bluesky.eh2.move_detector_stage as mvstgpln


def setup_detector(
    diffractometer: FourCircleDiffractometer, det_z: float, two_theta: float
) -> MsgGenerator:
    """Runs setup tasks prior to data collection. Currently, moves the diffractometer\
        an inputted distance in the X and Two-Theta axis.
        Args:
            detector_stage : Diffractometer object
            det_z : Float
                Distance to move in Z axis
            two_theta : Float
                (default 0.0)
                Distance to move in Two-Theta axis"""

    logger.info("Moving detector stage into position")
    yield from mvstgpln.move_stage(diffractometer.det_stage, det_z, two_theta)
