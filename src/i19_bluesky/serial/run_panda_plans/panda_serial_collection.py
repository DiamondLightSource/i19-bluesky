import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from dodal.devices.motors import XYZPhiStage
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.parameters.devices_composites import SerialCollectionEh2PandaComposite
from i19_bluesky.parameters.serial_parameters import SerialExperimentEh2
from i19_bluesky.serial.device_setup_plans.diffractometer_plans import (
    move_sample_stage_back,
    move_stage_x_and_z,
    setup_sample_stage,
)
from i19_bluesky.serial.panda_setup_plans.panda_setup_plans import (
    reset_panda,
    setup_panda_for_rotation,
)
from i19_bluesky.serial.panda_setup_plans.panda_stubs import arm_panda, disarm_panda


def trigger_panda(
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
    yield from setup_sample_stage(
        parameters.panda_rotation_params,
        devices.serial_stages,
    )
    yield from setup_panda_for_rotation(
        parameters.panda_rotation_params,
        devices.panda,
    )
    LOGGER.info("Arm panda and move phi")
    yield from arm_panda(devices.panda)
    LOGGER.info("Arm eiger")
    yield from bps.trigger(devices.eiger.drv.detector.arm)
    # Currently a test, will be modified as we solidify parameters going forwards
    # assumes a dictionary of integer keys and coordinates in a list
    for well_num, coords in parameters.well_position.items():
        yield from move_stage_x_and_z(coords[0], coords[2], devices.serial_stages)
        LOGGER.info(f"Moved to well {well_num}")
        if well_num % 2 == 0:
            LOGGER.info(
                f"Rotate {parameters.rot_axis_start} to\
                {parameters.panda_rotation_params.scan_end_deg}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi,
                parameters.panda_rotation_params.scan_end_deg,
                wait=True,
            )
        else:
            LOGGER.info(
                f"Rotate {parameters.panda_rotation_params.scan_end_deg} to\
                    {parameters.rot_axis_start}"
            )
            yield from bps.abs_set(
                devices.diffractometer.phi, parameters.rot_axis_start, wait=True
            )


def end_run(
    rot_axis_start: float,
    panda: HDFPanda,
    eiger: EigerDetector,
    serial_stages: XYZPhiStage,
):
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(eiger.drv.detector.disarm)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)
    yield from move_sample_stage_back(serial_stages, rot_axis_start)


def run_on_collection_abort(
    panda: HDFPanda,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(eiger.drv.detector.disarm)
    yield from disarm_panda(panda)
