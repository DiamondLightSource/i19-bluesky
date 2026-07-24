import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_stage_x_and_z,
)
from i19_bluesky.serial.panda_plans.panda_setup_plans import (
    setup_panda_for_rotation,
)
from i19_bluesky.serial.panda_plans.panda_stubs import arm_panda


def trigger_panda_collection(
    parameters: SerialExperimentEh2,
    devices: SerialCollectionEh2PandaComposite,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        parameters (SerialExperimentEh2): SerialExperimentEh2 object containing:
            well_positions (dict): Input coordinates of the selected wells
                (Key=well (int), value=X,Y,Z coordinates (list of ints))
            rot_axis_start (float): Starting phi position, in degrees.
            images_per_well (int): Number of images to take.
            exposure_time_s (float): Time between images, in seconds.
        devices (SerialCollectionEh2PandaComposite): SerialCollectionEh2PandaComposite
            object containing:
            diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
            panda (HDFPanda): The fastcs PandA ophyd device.
            eiger (EigerDetector): The eiger detector device
    """
    yield from setup_panda_for_rotation(
        parameters.panda_rotation_params,
        devices.panda,
    )
    LOGGER.info("Arm panda and move phi")
    yield from arm_panda(devices.panda)
    LOGGER.info("Kickoff eiger")
    yield from bps.kickoff(devices.eiger, wait=True)
    for i, (well_num, coords) in enumerate(parameters.wells_to_collect.items()):
        yield from move_stage_x_and_z(coords[0], coords[2], devices.serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        if i % 2 == 0:  # even in list
            LOGGER.info(
                f"Rotate {parameters.panda_rotation_params.scan_start_deg} to\
                {parameters.panda_rotation_params.scan_end_deg}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi,
                parameters.panda_rotation_params.scan_end_deg,
                wait=True,
            )
        else:  # odd idx in list
            LOGGER.info(
                f"Rotate {parameters.panda_rotation_params.scan_end_deg} to\
                    {parameters.panda_rotation_params.scan_start_deg}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi,
                parameters.panda_rotation_params.scan_start_deg,
                wait=True,
            )
    LOGGER.debug("Complete")
    yield from bps.complete(devices.eiger, wait=True)
