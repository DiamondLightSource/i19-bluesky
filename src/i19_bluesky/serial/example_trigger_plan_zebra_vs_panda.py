import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.serial.panda_setup_plans import setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda
from i19_bluesky.serial.zebra_collection_setup_plan import (
    setup_out_triggers,
    setup_zebra_for_collection,
    setup_zebra_for_triggering,
)


def setup_diffractometer(
    phi_start: float,
    phi_steps: int,
    exposure_time: int,
    diffractometer: FourCircleDiffractometer,
) -> MsgGenerator:
    """Setup phi on the diffractometer"""
    yield from bps.abs_set(diffractometer.phi.user_setpoint, phi_start)
    velocity = phi_steps / exposure_time
    yield from bps.abs_set(diffractometer.phi.velocity, velocity)


# phi_ramp_start = phi_start - 1


def setup_zebra(
    zebra: Zebra,
    phi_end,
    diffractometer: FourCircleDiffractometer,
    direction: RotationDirection,
):
    yield from setup_diffractometer(0, 0, 0, diffractometer)
    yield from setup_zebra_for_collection(
        zebra,
        direction,
        0,
        0,
        0,
    )
    yield from setup_out_triggers(zebra)
    yield from setup_zebra_for_triggering(zebra)
    arm_zebra(zebra)
    yield from bps.abs_set(diffractometer.phi.user_setpoint, phi_end)
    disarm_zebra(zebra)


def trigger_panda(
    panda: HDFPanda, diffractometer: FourCircleDiffractometer, phi_start, phi_end
):
    yield from setup_diffractometer(0, 0, 0, diffractometer)
    yield from setup_panda_for_rotation(panda, 0, 0, 0, 0, 0)
    yield from arm_panda(panda)
    yield from bps.abs_set(diffractometer.phi.user_setpoint, phi_end)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi.user_setpoint, phi_start)
    yield from disarm_panda(panda)
