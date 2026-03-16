"""
Example trigger plan ZEBRA vs PandA.
"""

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from bluesky.utils import MsgGenerator
from dodal.common import inject
from dodal.devices.beamlines.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.log import LOGGER
from i19_bluesky.serial.run_serial_with_panda import (
    move_diffractometer_back,
    setup_diffractometer,
)
from i19_bluesky.serial.zebra_collection_setup_plan import setup_zebra_for_collection

RAMP = 0.5


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
    gate_start = phi_start - RAMP
    gate_end = phi_end + RAMP
    yield from setup_diffractometer(
        diffractometer,
        gate_start,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Setup zebra for collection in the positive direction and arm")
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.POSITIVE, gate_start, gate_width, pulse_width
    )
    yield from arm_zebra(zebra)
    yield from bps.abs_set(diffractometer.phi, phi_end, wait=True)
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(zebra)

    yield from setup_diffractometer(
        diffractometer,
        gate_end,
        phi_steps,
        exposure_time,
    )
    LOGGER.info("Setup zebra for collection in the negative direction and arm")
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.NEGATIVE, gate_start, gate_width, pulse_width
    )
    yield from arm_zebra(zebra)
    yield from bps.abs_set(diffractometer.phi, phi_start, wait=True)
    LOGGER.info("Disarm zebra")
    yield from disarm_zebra(zebra)


def abort_zebra(diffractometer: FourCircleDiffractometer, zebra: Zebra) -> MsgGenerator:
    LOGGER.warning("ABORT")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_zebra(zebra)


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
        final_plan=lambda: (
            yield from move_diffractometer_back(diffractometer, phi_start)
        ),
        auto_raise=False,
    )
