"""
Example trigger plan ZEBRA vs PandA.
"""

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.log import LOGGER
from i19_bluesky.serial.panda_setup_plans import setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda
from i19_bluesky.serial.zebra_collection_setup_plan import setup_zebra_for_collection


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


def trigger_zebra(
    zebra: Zebra,
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    gate_width: float,
    pulse_width: float,
) -> MsgGenerator:
    """Trigger zebra for collection in the forward and backward direction.
    Gate start is calculated as phi start - 0.5.
    Gate end is calculated as phi end + 0.5.

    Args:
        zebra (Zebra): The zebra ophyd device.
        diffractometer (FourCircleDiffractometer): The diffractometer ophyd device.
        phi_start (float): Starting phi position, in degrees.
        phi_end (float): Ending phi position, in degrees.
        phi_steps (int): Number of images to take.
        exposure_time (float): Time between images, in seconds.
        gate_width (float): Total distance from gate_start to gate_end, in degrees.
        pulse_width (float): Value comes from change in degrees of scan/velocity,\
        in seconds.

    """
    gate_start = phi_start - 0.5
    gate_end = phi_end + 0.5
    yield from setup_diffractometer(
        diffractometer,
        gate_start,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Arm zebra and setup for positive direction collection")
    yield from arm_zebra(zebra)
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.POSITIVE, gate_start, gate_width, pulse_width
    )
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(zebra)

    yield from setup_diffractometer(
        diffractometer,
        gate_end,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Arm zebra and setup for negative direction collection")
    yield from arm_zebra(zebra)
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.NEGATIVE, gate_start, gate_width, pulse_width
    )
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(zebra)


def trigger_panda(
    panda: HDFPanda,
    diffractometer: FourCircleDiffractometer,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
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
    yield from arm_panda(panda)
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm panda")
    yield from disarm_panda(panda)


def abort_zebra(diffractometer: FourCircleDiffractometer, zebra: Zebra) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_zebra(zebra)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)


def move_diffractometer_back(diffractometer: FourCircleDiffractometer) -> MsgGenerator:
    LOGGER.info("Move diffractometer back to start position")
    yield from bps.abs_set(diffractometer.phi, 19, wait=True)


def run_panda_test(
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_panda(
            panda,
            diffractometer,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
        ),
        except_plan=lambda: (yield from abort_panda(diffractometer, panda)),
        final_plan=lambda: (yield from move_diffractometer_back(diffractometer)),
        auto_raise=False,
    )


def run_zebra_test(
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    gate_width: float,
    pulse_width: float,
    zebra: Zebra = inject("zebra"),
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_zebra(
            zebra,
            diffractometer,
            phi_start,
            phi_end,
            phi_steps,
            exposure_time,
            gate_width,
            pulse_width,
        ),
        except_plan=lambda: (yield from abort_zebra(diffractometer, zebra)),
        final_plan=lambda: (yield from move_diffractometer_back(diffractometer)),
        auto_raise=False,
    )
