import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.fastcs.eiger import EigerDetector
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.diffractometer_plans import (
    move_stage_x_and_z,
    setup_diffractometer,
)
from i19_bluesky.serial.panda_setup_plans import reset_panda, setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda


def trigger_panda(
    params: dict,
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
        params (dict): Input coordinates of the selected wells
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
    for well_num, coords in params.items():
        yield from move_stage_x_and_z(coords[0], coords[2], diffractometer)
        LOGGER.info(f"Moved to well {well_num}")
        if well_num % 2 == 0:
            LOGGER.info(f"Rotating {phi_start} to {phi_end}")
            yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
            yield from bps.sleep(2.0)
        else:
            LOGGER.info(f"Rotating {phi_end} to {phi_start}")
            yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
            yield from bps.sleep(2.0)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    LOGGER.info("Disarm eiger")
    yield from bps.trigger(eiger.drv.detector.disarm)
    yield from reset_panda(panda)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)
