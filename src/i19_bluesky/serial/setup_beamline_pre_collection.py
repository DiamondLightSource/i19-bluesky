from bluesky.log import logger
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.eh2.backlight_plan import move_backlight_out
from i19_bluesky.eh2.move_detector_stage import move_detector_stage
from i19_bluesky.eh2.pincol_control_plans import move_pin_col_to_requested_in_position


def setup_beamline_before_collection(
    det_z: float,
    two_theta: float,
    backlight: BacklightPosition,
    diffractometer: FourCircleDiffractometer,
    pinhole_collimator: PinholeCollimatorControl,
    aperture: PinColRequest,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection. Currently, moves the backlight to its\
        'out' position, then moves the pinhole collimator to position to record at the \
        requested aperture, a placeholder for moving the attenutator wedge, followed by\
        a command to move the diffractometer an inputted distance in the X and Two-Theta
        axis.
        Args:
            det_z : Float
                Distance to move in Z axis
            two_theta : Float
                (default 0.0)
                Distance to move in Two-Theta axis
            backlight : Backlight controller object
            diffractometer : Diffractometer object
            pinhole_collimator : Pinhole Collimator control object
            aperture : PinColRequest object (StrEnum)
"""
    logger.info("Moving backlight out")
    yield from move_backlight_out(backlight)
    logger.info("Moving pinhole collimator into position")
    yield from move_pin_col_to_requested_in_position(aperture, pinhole_collimator)
    logger.info("Moving attenuator wedge")
    ###TODO: find or write this
    logger.info("Moving detector stage into position")
    yield from move_detector_stage(diffractometer.det_stage, det_z, two_theta)
