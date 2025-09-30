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
    EncEnum,
    RotationDirection,
    TrigSource,
    Zebra,
)

from i19_bluesky.log import LOGGER

PULSE_WIDTH: float = 0.002


def setup_zebra_for_collection(
    zebra: Zebra,
    direction: RotationDirection,
    gate_start: float,
    gate_width: float,
    group: str = "setup_zebra_for_collection",
    wait: bool = True,
):
    LOGGER.debug("Setup ZEBRA for collection.")
    pulse_start = gate_start + 0.02

    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)
    yield from bps.abs_set(zebra.pc.num_gates, 1, group=group)

    yield from bps.abs_set(zebra.pc.pulse_start, pulse_start, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, PULSE_WIDTH, group=group)

    yield from bps.abs_set(zebra.pc.dir, direction, group=group)

    yield from setup_zebra_for_triggering(zebra)
    yield from setup_out_triggers(zebra)

    if wait:
        yield from bps.wait(group)


def setup_out_triggers(
    zebra: Zebra,
    group: str = "setup_out_triggers",
    wait: bool = True,
):
    yield from bps.abs_set(
        zebra.output.out_pvs[1], zebra.mapping.sources.OR1, group=group
    )
    yield from bps.abs_set(
        zebra.output.out_pvs[2], zebra.mapping.sources.PC_PULSE, group=group
    )

    if wait:
        yield from bps.wait(group)


def setup_zebra_for_triggering(
    zebra: Zebra,
    group: str = "setup_zebra_for_triggering",
    wait: bool = True,
):
    LOGGER.debug(
        "Setup ZEBRA to trigger the gate and pulse signals and specify the"
        "encoder in use."
    )
    yield from bps.abs_set(zebra.pc.gate_source, TrigSource.POSITION, group=group)
    yield from bps.abs_set(zebra.pc.gate_trigger, EncEnum.ENC1, group=group)
    yield from bps.abs_set(zebra.pc.pulse_source, TrigSource.TIME, group=group)

    if wait:
        yield from bps.wait(group)
