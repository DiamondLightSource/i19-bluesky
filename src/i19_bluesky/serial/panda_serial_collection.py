import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.diffractometer_plans import (
    move_stage_x_and_z,
    setup_diffractometer,
)
from i19_bluesky.serial.panda_setup_plans import reset_panda, setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda


def trigger_panda(
    det_z: float,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer,
    panda: HDFPanda,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        panda (HDFPanda): The fastcs PandA ophyd device.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
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
    yield from arm_panda(panda)  # move in X
    # for X
    yield from move_stage_x_and_z(100, det_z, diffractometer)
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    yield from bps.sleep(2.0)
    yield from move_stage_x_and_z(100, det_z, diffractometer)
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    yield from reset_panda(panda)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)
