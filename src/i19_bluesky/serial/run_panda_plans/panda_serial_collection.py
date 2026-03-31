import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.serial_parameters import DeviceInput, SerialExperiment
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_diffractometer_back,
    move_stage_x_and_z,
    setup_diffractometer,
)
from i19_bluesky.serial.panda_setup_plans.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)
from i19_bluesky.serial.panda_setup_plans.panda_stubs import arm_panda, disarm_panda


def trigger_panda(
    parameters: SerialExperiment,
    devices: DeviceInput,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        parameters (SerialExperiment): SerialExperiment or dict containing:
            well_positions (dict): Input coordinates of the selected wells
                (Key=well (int), value=X,Y,Z coordinates (list of ints))
            rot_axis_start (float): Starting phi position, in degrees.
            rot_axis_end (float): Ending phi position, in degrees.
            images_per_well (int): Number of images to take.
            exposure_time_s (float): Time between images, in seconds.
        devices (DeviceInput): DeviceInput object containing:
            diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
            panda (HDFPanda): The fastcs PandA ophyd device.
            eiger (EigerDetector): The eiger detector device
    """
    yield from setup_diffractometer(
        parameters,
        devices.diffractometer,
    )
    yield from setup_panda_for_rotation(
        parameters,
        devices.panda,
    )
    LOGGER.info("Arm panda and move phi")
    yield from arm_panda(devices.panda)
    LOGGER.info("Arm eiger")
    yield from bps.trigger(devices.eiger.drv.detector.arm)
    # Currently a test, will be modified as we solidify parameters going forwards
    # assumes a dictionary of integer keys and coordinates in a list
    for well_num, coords in parameters.well_position.items():
        yield from move_stage_x_and_z(coords[0], coords[2], devices.diffractometer)
        LOGGER.info(f"Moved to well {well_num}")
        if well_num % 2 == 0:
            LOGGER.info(
                f"Rotate {parameters.rot_axis_start} to {parameters.rot_axis_end}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi, parameters.rot_axis_end, wait=True
            )
        else:
            LOGGER.info(
                f"Rotate {parameters.rot_axis_end} to {parameters.rot_axis_start}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi, parameters.rot_axis_start, wait=True
            )


def end_run(
    parameters: SerialExperiment,
    devices: DeviceInput,
):
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(devices.eiger.drv.detector.disarm)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(devices.panda)
    yield from reset_panda(devices.panda)
    yield from move_diffractometer_back(
        devices.diffractometer, parameters.rot_axis_start
    )


def run_on_collection_abort(devices: DeviceInput) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(devices.diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(devices.eiger.drv.detector.disarm)
    yield from disarm_panda(devices.panda)
