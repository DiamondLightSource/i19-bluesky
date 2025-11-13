import bluesky.plan_stubs as bps
from dodal.devices.i19.diffractometer import FourCircleDiffractometer
from dodal.devices.zebra.zebra import RotationDirection, Zebra

from i19_bluesky.eh2.zebra_arming_plan import arm_zebra, disarm_zebra
from i19_bluesky.serial.diffractometer_setup import setup_diffractometer
from i19_bluesky.serial.zebra_collection_setup_plan import (
    setup_out_triggers,
    setup_zebra_for_collection,
    setup_zebra_for_triggering,
)

setup_diffractometer(
    phi_start=0,
    phi_steps=0,
    exposure_time=0,
    phi_velocity=0,
    diffractometer=FourCircleDiffractometer,
)

# def_phi_ramp_start(phi_start, phi_ramp_start):
# phi_ramp_start = phi_start - 1


def setup_zebra_positive(zebra: Zebra, phi_end, phi_value):
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.POSITIVE, 0, 0, 0, "setup_zebra_for_collection", True
    )
    yield from setup_out_triggers(zebra, "setup_out_triggers", True)
    yield from setup_zebra_for_triggering(zebra, "setup_zebra_for_triggering")
    arm_zebra(zebra)
    yield from bps.abs_set(phi_value, phi_end)
    disarm_zebra(zebra)


def setup_zebra_negative(zebra: Zebra, phi_end, phi_value):
    yield from setup_zebra_for_collection(
        zebra, RotationDirection.NEGATIVE, 0, 0, 0, "setup_zebra_for_collection", True
    )
    yield from setup_out_triggers(zebra, "setup_out_triggers", True)
    yield from setup_zebra_for_triggering(zebra, "setup_zebra_for_triggering")
    arm_zebra(zebra)
    yield from bps.abs_set(phi_value, phi_end)
    disarm_zebra(zebra)
