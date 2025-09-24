"""
i19-2 Zebra setup plan for collection.

Input parameters include: rotation direction, PC gate and pulse setting details.
The plan sets the triggering source for the gate a pulse signals, as position and time
respectively and specifies the zebra encoder in use.
The plan can only go in the positive or negative direction at once since the zebra box
cannot go from high to low without disarming and resetting it.
"""

import bluesky.plan_stubs as bps
from dodal.devices.zebra.zebra import (
    RotationDirection,
    Zebra,
)

from i19_bluesky.log import LOGGER

pulse_width: float = 0.00002


def setup_zebra_for_collection(
    zebra: Zebra,
    direction: RotationDirection,
    num_images: int,
    gate_start: float,
    gate_width: float,
    group: str = "setup_zebra_for_collection",
    wait: bool = True,
):
    LOGGER.debug("Setup ZEBRA for collection.")
    pulse_start = gate_start + 0.02

    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)
    yield from bps.abs_set(zebra.pc.num_gates, num_images, group=group)

    yield from bps.abs_set(zebra.pc.pulse_start, pulse_start, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, pulse_width, group=group)

    yield from bps.abs_set(zebra.pc.dir, direction, group=group)

    yield from bps.abs_set(
        zebra.output.out_pvs[zebra.mapping.outputs.OUT1_TTL], group=group
    )

    if wait:
        yield from bps.wait(group)


def setup_zebra_for_triggering(
    zebra: Zebra,
    group: str = "setup_zebra_for_triggering",
    wait: bool = True,
):
    yield from bps.abs_set(zebra.pc.gate_source, "Position", group=group)
    yield from bps.abs_set(zebra.pc.gate_trigger, "Enc1", group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, "Time", group=group)

    if wait:
        yield from bps.wait(group)
