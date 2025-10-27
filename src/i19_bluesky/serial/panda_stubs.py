import bluesky.plan_stubs as bps
from bluesky.utils import MsgGenerator
from ophyd_async.fastcs.panda import PandaBitMux

from i19_bluesky.log import LOGGER

# from i19_bluesky.serial.setup_panda import load_panda_from_yaml (issue 91 still to do
# owing to beamline poweroff)
from i19_bluesky.serial.setup_panda import (
    CustomPanda,
    arm_panda,
    disarm_panda,
    generate_panda_seq_table,
)

DEG_TO_ENC_COUNTS = 1000
GENERAL_TIMEOUT = 60


def setup_panda_for_rotation(
    panda: CustomPanda,
    phi_ramp_start,
    phi_start,
    phi_end,
    phi_steps,
    time_between_images,
) -> MsgGenerator:
    """Configures the PandA device for phi forward and backward rotation"""

    # yield from bps.stage(panda, group="panda-setup")
    # yield from load_panda_from_yaml(panda) (issue 91)

    # Home the input encoder
    yield from bps.abs_set(
        panda.inenc[1].val,
        phi_ramp_start * DEG_TO_ENC_COUNTS,
        wait=True,
    )

    seq_table = generate_panda_seq_table(
        phi_start, phi_end, phi_steps, time_between_images
    )

    yield from bps.abs_set(panda.seq[1].table, seq_table, group="panda-setup")

    # Values need to be set before blocks are enabled, so wait here
    yield from bps.wait(group="panda-setup", timeout=GENERAL_TIMEOUT)

    LOGGER.info(f"PandA sequencer table has been set to: {str(seq_table)}")
    seq_table_readback = yield from bps.rd(panda.seq[1].table)
    LOGGER.debug(f"PandA sequencer table readback is: {str(seq_table_readback)}")

    yield from arm_and_disarm_panda(panda)
    yield from reset_panda(panda)


def arm_and_disarm_panda(panda: CustomPanda, group="arm_panda_rotation"):
    yield from arm_panda(panda)
    yield from bps.abs_set(panda.outenc[1].val, PandaBitMux.ZERO, group=group)
    yield from bps.abs_set(panda.outenc[2].val, panda.inenc[1].val, group=group)
    yield from disarm_panda(panda)


def reset_panda(panda: CustomPanda, group="reset_panda"):
    yield from bps.abs_set(panda.outenc[1].val, panda.inenc[1].val, group=group)
    yield from bps.abs_set(panda.outenc[2].val, panda.inenc[2].val, group=group)
