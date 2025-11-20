import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra
from ophyd_async.fastcs.panda import HDFPanda

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.serial.panda_setup_plans import setup_panda_for_rotation
from i19_bluesky.serial.panda_stubs import arm_panda, disarm_panda
from i19_bluesky.serial.zebra_collection_setup_plan import setup_zebra_for_collection


def setup_diffractometer(
    ramp_value: float,
    phi_steps: int,
    exposure_time: int,
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
    exposure_time: int,
    diffractometer: FourCircleDiffractometer,
    gate_width: float,
    pulse_width: float,
) -> MsgGenerator:
    """Trigger zebra for collection in the forward (+ve) and backward (-ve) direction"""
    gate_start = phi_start - 1  # phi_ramp_start
    gate_end = phi_end + 1  # phi_ramp_end
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
    time_between_images,
):
    yield from setup_diffractometer(phi_start, phi_steps, exposure_time, diffractometer)
    yield from setup_panda_for_rotation(
        panda,
        phi_ramp_start,
        phi_start,
        phi_end,
        phi_steps,
        time_between_images,
    )
    yield from arm_panda(panda)
    yield from bps.abs_set(diffractometer.phi, phi_end)
    yield from bps.sleep(2.0)
    yield from bps.abs_set(diffractometer.phi, phi_start)
    yield from disarm_panda(panda)
