"""
i19-2 Zebra setup plan for serial collection.
"""

import bluesky.plan_stubs as bps
from dodal.devices.zebra.zebra import (
    EncEnum,
    RotationDirection,
    TrigSource,
    Zebra,
)

from i19_bluesky.log import LOGGER

PULSE_START: float = 0.02


def setup_zebra_for_collection(
    zebra: Zebra,
    direction: RotationDirection,
    gate_start: float,
    gate_width: float,
    pulse_width: float,  # value from: change in degrees of scan/velocity
    group: str = "setup_zebra_for_collection",
    wait: bool = True,
):
    """
    Setup the i19-2 zebra for serial collection.

    Input parameters include: rotation direction, PC gate and pulse setting details.
    The plan sets the triggering source for the gate and pulse, as position and time \
    respectively and specifies the zebra encoder in use.
    Pulse step is calculated as pulse width + 0.1.
    The plan can only go in the positive or negative direction at once since the zebra \
    box cannot go from high to low without disarming and resetting it.
    """
    LOGGER.debug("Setup ZEBRA for collection.")
    pulse_step = pulse_width + 0.1

    yield from bps.abs_set(zebra.pc.gate_start, gate_start, group=group)
    yield from bps.abs_set(zebra.pc.gate_width, gate_width, group=group)
    yield from bps.abs_set(zebra.pc.num_gates, 1, group=group)

    yield from bps.abs_set(zebra.pc.pulse_start, PULSE_START, group=group)
    yield from bps.abs_set(zebra.pc.pulse_width, pulse_width, group=group)
    yield from bps.abs_set(zebra.pc.pulse_step, pulse_step, group=group)

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
