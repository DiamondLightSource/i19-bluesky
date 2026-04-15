from bluesky.utils import MsgGenerator

from i19_bluesky.eh2.backlight_plan import move_backlight_out
from i19_bluesky.eh2.pincol_control_plans import move_pin_col_to_requested_in_position
from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_detector_stage,
)


def setup_beamline_before_collection(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Runs setup tasks prior to data collection. Currently, moves the backlight to its
    'out' position, then moves the pinhole collimator to position to record at the
    requested aperture, a placeholder for moving the attenutator wedge, followed by
    a command to move the diffractometer an inputted distance in the X and Two-Theta
    axis.

    Args:
        parameters (SerialExperimentEh2) : SerialExperimentEh2 object
        devices (SerialCollectionEh2PandaComposite) : SerialCollectionEh2PandaComposite
        object
    """
    LOGGER.info("Moving backlight out")
    yield from move_backlight_out(devices.backlight)
    LOGGER.info("Moving pinhole collimator into position")
    yield from move_pin_col_to_requested_in_position(
        parameters.aperture_request, devices.pincol
    )
    LOGGER.info("Moving attenuator wedge")
    # waiting for https://github.com/DiamondLightSource/i19-bluesky/issues/8
    LOGGER.info("Moving detector stage into position")
    yield from move_detector_stage(
        devices.diffractometer.det_stage,
        parameters.detector_distance_mm,
        parameters.two_theta_deg,
    )
