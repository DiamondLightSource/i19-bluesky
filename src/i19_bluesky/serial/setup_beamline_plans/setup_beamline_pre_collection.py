from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.backlight import BacklightPosition
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.beamlines.i19.pin_col_stages import (
    PinColRequest,
    PinholeCollimatorControl,
)

from i19_bluesky.eh2.backlight_plan import move_backlight_out
from i19_bluesky.eh2.pincol_control_plans import move_pin_col_to_requested_in_position
from i19_bluesky.log import LOGGER
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


def setup_beamline_before_collection(
    aperture_request: PinColRequest,
    detector_distance_mm: float,
    two_theta_deg: float,
    backlight: BacklightPosition,
    pincol: PinholeCollimatorControl,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection. Currently, moves the backlight to its
    'out' position, then moves the pinhole collimator to position to record at the
    requested aperture, a placeholder for moving the attenutator wedge, followed by
    a command to move the diffractometer an inputted distance in the X and Two-Theta
    axis.

    Args:
        aperture_request (PinColRequest):
            Requested position of aperture
        detector_distance_mm (float):
            Distance to move in the X axis
        two_theta_deg (float):
            Angle to move to in the theta axis
        backlight (BacklightPosition):
            Backlight device
        pincol (PinholeCollimatorControl):
            Pinhole Collimator device
        diffractometer (FourCircleDiffractometer):
            Diffractometer device
    """
    LOGGER.info("Moving backlight out")
    yield from move_backlight_out(backlight)
    LOGGER.info("Moving pinhole collimator into position")
    yield from move_pin_col_to_requested_in_position(aperture_request, pincol)
    LOGGER.info("Moving attenuator wedge")
    # waiting for https://github.com/DiamondLightSource/i19-bluesky/issues/8
    LOGGER.info("Moving detector stage into position")
    yield from move_detector_stage(
        diffractometer.det_stage,
        detector_distance_mm,
        two_theta_deg,
    )
