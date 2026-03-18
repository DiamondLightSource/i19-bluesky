import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import (
    FourCircleDiffractometer,
)
from ophyd_async.fastcs.eiger import EigerController
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.log import LOGGER
from i19_bluesky.serial.panda_setup_plans import reset_panda, setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda


def setup_diffractometer(
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_steps: int,
    exposure_time: float,
) -> MsgGenerator:
    """Setup phi start posistion and velocity on the diffractometer.

    Args:
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position.
        phi_steps (int): Number of images to take.
        exposure_time(float): Time between images, in seconds."""
    yield from bps.abs_set(diffractometer.phi, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(diffractometer.phi.velocity, velocity)


def trigger_panda(
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    panda: HDFPanda,
    diffractometer: FourCircleDiffractometer,
    eiger: EigerController,
) -> MsgGenerator:
    """Trigger panda for collection in both directions.

    Args:
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
        panda (HDFPanda): The fastcs PandA ophyd device.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        eiger (EigerController): The eiger device
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
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    LOGGER.info("Arm eiger")
    # This is strange but it seems to work. Passes the tests - await didn't work as
    # I'm sure there's a better way to do it (or maybe I'm calling the wrong Eiger)
    armed = eiger.arm()
    LOGGER.info(armed)
    # LOGGER.info(armed)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)
    LOGGER.info("Disarm eiger")
    disarmed = eiger.disarm()
    LOGGER.info(disarmed)
    yield from reset_panda(panda)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)


def move_diffractometer_back(
    diffractometer: FourCircleDiffractometer, phi_start: float
) -> MsgGenerator:
    LOGGER.info("Move diffractometer back to start position")
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)


def run_panda_test(
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    panda: HDFPanda = inject("panda"),
    eiger: EigerController = inject("eiger"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_panda(
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            panda,
            diffractometer,
            eiger,
        ),
        except_plan=lambda: (yield from abort_panda(diffractometer, panda)),
        final_plan=lambda: (
            yield from move_diffractometer_back(diffractometer, phi_start)
        ),
        auto_raise=False,
    )
