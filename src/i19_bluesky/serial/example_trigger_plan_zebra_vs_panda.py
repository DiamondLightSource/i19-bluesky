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
    ramp_value: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Setup phi on the diffractometer"""
    yield from bps.abs_set(diffractometer.phi, ramp_value)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(diffractometer.phi.velocity, velocity)


def trigger_zebra(
    zebra: Zebra,
    phi_start: float,
    phi_end: float,
    phi_steps: int,
    exposure_time: float,
    diffractometer: FourCircleDiffractometer,
    gate_width: float,
    pulse_width: float,
) -> MsgGenerator:
    """Trigger zebra for collection in the forward (+ve) and backward (-ve) direction"""
    gate_start = phi_start - 0.5  # phi_ramp_start
    gate_end = phi_end + 0.5  # phi_ramp_end
    yield from setup_diffractometer(
        gate_start, phi_steps, exposure_time, diffractometer
    )
    yield from arm_zebra(zebra)
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.POSITIVE, gate_start, gate_width, pulse_width
    )
    yield from bps.abs_set(diffractometer.phi, phi_end)
    yield from disarm_zebra(zebra)

    yield from setup_diffractometer(gate_end, phi_steps, exposure_time, diffractometer)
    yield from arm_zebra(zebra)
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.NEGATIVE, gate_start, gate_width, pulse_width
    )
    yield from bps.abs_set(diffractometer.phi, phi_start)
    yield from disarm_zebra(zebra)


def trigger_panda(
    panda: HDFPanda,
    diffractometer: FourCircleDiffractometer,
    phi_ramp_start,
    phi_start,
    phi_end,
    phi_steps,
    exposure_time,
):
    yield from setup_diffractometer(phi_start, phi_steps, exposure_time, diffractometer)
    yield from setup_panda_for_rotation(
        panda,
        phi_ramp_start,
        phi_start,
        phi_end,
        phi_steps,
        exposure_time,
    )
    yield from arm_panda(panda)
    yield from bps.abs_set(diffractometer.phi, phi_end)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi, phi_start)
    yield from disarm_panda(panda)


def abort_zebra(diffractometer: FourCircleDiffractometer, zebra: Zebra) -> MsgGenerator:
    LOGGER.warning("I AM ABORTING")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_zebra(zebra)


def abort_panda(
    diffractometer: FourCircleDiffractometer, panda: HDFPanda
) -> MsgGenerator:
    LOGGER.warning("I AM ABORTING")
    yield from bps.abs_set(diffractometer.phi.motor_stop, 1, wait=True)
    yield from disarm_panda(panda)


def move_diffractometer_back(diffractometer: FourCircleDiffractometer) -> MsgGenerator:
    LOGGER.info("Move diffractometer back to where it was")
    yield from bps.abs_set(diffractometer.phi, 19, wait=True)


def run_panda_test(
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    panda: HDFPanda = inject("panda"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_panda(panda, diffractometer, 19.5, 20, 23, 30, 0.1),
        except_plan=lambda: (yield from abort_panda(diffractometer, panda)),
        final_plan=lambda: (yield from move_diffractometer_back(diffractometer)),
        auto_raise=False,
    )


def run_zebra_test(
    diffractometer: FourCircleDiffractometer = inject("diffractometer"),
    zebra: Zebra = inject("zebra"),
) -> MsgGenerator:
    yield from bpp.contingency_wrapper(
        trigger_zebra(zebra, 20, 23, 30, 0.1, diffractometer, 3.1, 1),
        except_plan=lambda: (yield from abort_zebra(diffractometer, zebra)),
        final_plan=lambda: (yield from move_diffractometer_back(diffractometer)),
        auto_raise=False,
    )
