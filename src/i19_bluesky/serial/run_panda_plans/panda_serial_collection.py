import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
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
    well_positions,  # Currently a test, will be modified as we solidify parameters
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer,
    panda: HDFPanda,
    eiger: EigerDetector,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        well_positions: Input coordinates of the selected wells
            (Key=well (int), value=X,Y,Z coordinates (list of ints))
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        panda (HDFPanda): The fastcs PandA ophyd device.
        eiger (EigerDetector): The eiger detector device
    """
    yield from setup_diffractometer(
        diffractometer,
        phi_start,
        phi_steps,
        exposure_time,
    )
    yield from setup_panda_for_rotation(
        panda,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Arm panda and move phi")
    yield from arm_panda(panda)
    LOGGER.info("Arm eiger")
    yield from bps.trigger(eiger.drv.detector.arm)
    # Currently a test, will be modified as we solidify parameters going forwards
    # assumes a dictionary of integer keys and coordinates in a list
    for well_num, coords in well_positions.items():
        yield from move_stage_x_and_z(coords[0], coords[2], diffractometer)
        LOGGER.info(f"Moved to well {well_num}")
        if well_num % 2 == 0:
            LOGGER.info(f"Rotating {phi_start} to {phi_end}")
            yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
        else:
            LOGGER.info(f"Rotating {phi_end} to {phi_start}")
            yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)


def end_run(
    panda: HDFPanda,
    eiger: EigerDetector,
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
):
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(eiger.drv.detector.disarm)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)
    yield from move_diffractometer_back(diffractometer, phi_start)


def run_on_collection_abort(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda, eiger: EigerDetector
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from bps.trigger(eiger.drv.detector.disarm)
    yield from disarm_panda(panda)
